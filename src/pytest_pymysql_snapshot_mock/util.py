import enum
import pickle
import re
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, cast

from pytest import FixtureRequest


class Mode(enum.Enum):
    """An enumeration of the available modes.

    The available modes are ``STORE_DATA``, ``MOCK`` and ``NORMAL``.
    """

    STORE_DATA = "Store Data"
    MOCK = "Mock"
    NORMAL = "Normal"


class DatabaseMock:
    """
    Properties and methods for the database mock fixture.

    Parameters
    ----------
    mode: `~pytest_pymysql_snapshot_mock.util.Mode`
        The mode in which the fixture is used.
    db_data_dir: `~pathlib.Path`
        Directory for storing the database snapshot files.
    request: `~pytest.FixtureRequest`
        pytest request fixture.

    Attributes
    ----------
    mode: `~pytest_pymysql_snapshot_mock.util.Mode`
        The mode in which the fixture is used.
    """

    def __init__(
        self,
        mode: Mode,
        db_data_dir: Path,
        request: FixtureRequest,
    ):
        self._mode = mode
        self._request = request
        self._data_dir = DatabaseMock._test_data_dir(db_data_dir, request)

        if mode == Mode.MOCK:
            self._data = self._read_data()
        else:
            self._data = defaultdict(list)

    @property
    def mode(self) -> Mode:  # noqa: D102
        return self._mode

    def user_value(self, value: Any) -> Any:
        """
        Mock a user-supplied value.

        Some database tests may generate random values, store these in the database and
        use these random values in assertions. This poses a problem for mocking as the
        value will be different for each test run, so that the current and the
        previously stored version differs. Hence such tests will fail when run with the
        stored data.

        The solution is to wrap random values with this method. For example:

        .. code:: python

           import uuid

           random_value = database_mock.user_value(str(uuid.uuid4())

        When database data is stored, ``value`` is stored along with the data, and it is
        returned as the return value. When the database is mocked, the previously stored
        stored value is returned. Otherwise the method just returns ``value``.

        It must be possible to pickle the passed value

        Parameters
        ----------
        value: any
            Value. The value is ignored when the database is mocked.

        Returns
        -------
        any
            Either the previously stored value (when the database is being mocked) or
            the passed value (otherwise).

        """
        if self._mode == Mode.STORE_DATA:
            self._data["user--stored-value"].append(value)
            return value
        elif self._mode == Mode.MOCK:
            return self._data["user--stored-value"].pop(0)
        elif self._mode == Mode.NORMAL:
            return value

    @staticmethod
    def _test_data_dir(db_data_dir: Path, request: FixtureRequest) -> Path:
        if not db_data_dir:
            return Path(tempfile.gettempdir())
        parent_dir = request.path.parent.relative_to(request.config.rootpath)
        return db_data_dir / parent_dir

    def _write_data(self) -> None:
        filepath = self._filepath()
        with open(filepath, "wb") as f:
            pickle.dump(self._data, f)

    def _read_data(self) -> Dict[str, List[Any]]:
        filepath = self._filepath()
        with open(filepath, "rb") as f:
            return cast(Dict[str, List[Any]], pickle.load(f))

    def _record_value(self, key: str, value: Any) -> None:
        self._data[key].append(value)

    def _read_value(self, key: str) -> Any:
        return self._data[key].pop(0)

    def _filepath(self) -> Path:
        # Adapted from the pytest-regressions source code
        basename = re.sub(r"[\W]", "_", self._request.node.name)
        self._data_dir.mkdir(parents=True, exist_ok=True)

        return self._data_dir / (basename + ".db")
