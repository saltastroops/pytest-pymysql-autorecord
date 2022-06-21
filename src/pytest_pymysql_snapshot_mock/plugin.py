import pickle
from collections import defaultdict
from typing import Any, List, Dict, Generator, cast

import pymysql
import pytest
import re
from pathlib import Path
from pytest import FixtureRequest, MonkeyPatch

from .connect import mock_connect
from .util import DatabaseMock, Mode



def pytest_addoption(parser):
    """
    Add the command line options for the plugin.

    Parameters
    ----------
    parser: `pytest.Parser`
        Option parser.
    """
    group = parser.getgroup("pytest-pymysql-snapshot-mock")
    group.addoption(
        "--store-db-data",
        action="store_true",
        dest="store_db_data",
        help="Store the database data in a file for mocking."
    )
    group.addoption(
        "--mock-db-data",
        action="store_true",
        dest="mock_db_data",
        help="Use previously stored data instead of connecting to the database."
    )


@pytest.fixture(autouse=True)
def database_mock(
    original_datadir: Path, request: FixtureRequest, monkeypatch: MonkeyPatch
) -> Generator[None, None, None]:
    """
    Mock PyMySQL's connect function.

    The behaviour of the mock connect function is chosen with a command line argument:

    * If pytest is run with the ``--store-db-data`` flag, PyMySQL's ``connect`` function
      is used for the database queries and the results are stored in a file. Existing
      files are overwritten.
    * If pytest is run with the ``--mock-db-data`` flag, no connection to a database is
      made and the previously stored data is used instead.
    * If neither the ``--store-db-data`` nor the ``--mock-db-data`` flag is used,
      PyMySQL's ``connect`` function is used without any changes.

    A test fails if you use the ``--mock-db-data`` flag, but no data has been stored for
    the test yet.

    The ``--store-db-data`` and ``--mock-db-data`` flag cannot be used together.

    Parameters
    ----------
    original_datadir: `~pathlib.Path`
        The directory containing the test file.
    request: `~pytest.FixtureRequest`
        The pytest request details.
    monkeypatch: `~pytest.MonkeyPatch`
        Object for monkeypatching.
    """
    is_storing = request.config.option.store_db_data
    is_mocking = request.config.option.mock_db_data

    if is_storing and is_mocking:
        pytest.fail("The command line flags --store-db-data and --mock-db-data are "
                    "mutually exclusive.")

    data: Dict[str, List[Any]] = {}
    if is_storing:
        mode = Mode.STORE_DATA
    elif is_mocking:
        mode = Mode.MOCK
    else:
        mode = Mode.NORMAL

    db_mock_fixture = DatabaseMock(mode, original_datadir, request)
    connect = mock_connect(db_mock_fixture, pymysql.connect)
    monkeypatch.setattr(pymysql, "connect", connect)

    yield db_mock_fixture

    if is_storing:
        db_mock_fixture._write_data()
