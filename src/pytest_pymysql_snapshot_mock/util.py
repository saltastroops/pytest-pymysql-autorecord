import enum
import pickle
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any, cast

from pytest import FixtureRequest


class Mode(enum.Enum):
    """An enumeration of the available modes."""

    STORE_DATA = "Store Data"
    MOCK = "Mock"
    NORMAL = "Normal"


class DatabaseMockFixture:
    """
    Properties and methods for the database mock fixture.

    Parameters
    ----------
    mode: `~pytest_pymysql_snapshot_mock.util.Mode`
        The mode in which the fixture is used.
    original_datadir: `~pathlib.Path`
        Directory containing the test file which is being executed.
    request: `~pytest.FixtureRequest`
        pytest request fixture.

    Attributes
    ----------
    mode: `~pytest_pymysql_snapshot_mock.util.Mode`
        The mode in which the fixture is used.
    """

    def __init__(self, mode: Mode, original_datadir: Path, request: FixtureRequest, ):
        self._mode = mode
        self._request = request
        self._original_datadir = original_datadir

        if mode == Mode.MOCK:
            self._data = self.read_data()
        else:
            self._data = defaultdict(list)

    @property
    def mode(self):
        return self._mode

    def user_value(self, value: Any) -> Any:
        if self._mode == Mode.STORE_DATA:
            self._data[f"user--stored-value"].append(value)
            return value
        elif self._mode == Mode.MOCK:
            return self._data[f"user--stored-value"].pop(0)
        elif self._mode == Mode.NORMAL:
            return value

    def write_data(self) -> None:
        filepath = self._filepath()
        with open(filepath, "wb") as f:
            pickle.dump(self._data, f)

    def read_data(self) -> Dict[str, List[Any]]:
        filepath = self._filepath()
        with open(filepath, "rb") as f:
            return cast(Dict[str, List[Any]], pickle.load(f))

    def record(self, key: str, value: Any) -> None:
        self._data[key].append(value)

    def read(self, key: str) -> Any:
        return self._data[key].pop(0)

    def _filepath(self) -> Path:
        # Adapted from the pytest-regressions source code
        basename = re.sub(r"[\W]", "_", self._request.node.name)
        self._original_datadir.mkdir(exist_ok=True)

        return self._original_datadir / (basename + ".db")

