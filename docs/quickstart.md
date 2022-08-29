# Quickstart

Most texts on software testing suggest, with good reason, to use mocking if the code under testing uses a database, or to create (fake) entries for the test.

While this generally is good advice, it isn't always feasible. If your database contains hundreds of tables, creating fake data may be more pain than gain.

Hence, there may be a point in testing against "real" data. This works fine while testing on your own machine with access to the real database. But the moment you want to run tests on, say, GitHub, you run into a snag. From a security point of view, GitHub shouldn't have access to your database.

One way to solve the issue would be to use a local CI/CD pipeline, such as setting up a workflow on Jenkins. Another option would be to disable such tests when run on GitHub, which would fly against the idea of Continuous Integration.

pytest-pymysql-snapshot-mock offers another way out of the dilemma, which is inspired by snapshot testing and by HTTP request interception. This plugin stores data returned by the database, and subsequently uses the stored data for mocking. You get the best of both world: You have the benefit of testing against real-world data, but you don't need the database when running tests on a remote server.

As the name suggests, pytest-pymysql-snapshot-mock is a pytest plugin for mocking PyMySQL. Other database drivers, whether for MySQL or not, are not supported.

## Before you use this plugin

Real-world business data has a tendency of being confidential. A stern warning is thus in order:

```{warning}
This plugin stores database data in files which are intended to be under version control and as such might end up under version control. Make sure you don't use it when requesting confidential data, or that the project using the plugin is not availsable on a public repository.
```

It might be a good idea to test against a database whose (still real-world) data has been sanitized, with confidential data such as email addresses and password hashes having been replaced.

There is a second caveat: pytest-pymysql-snapshot-mock assumes that, within a test, your database access is deterministic, i.e. database requests are always executed in the same order. More precisely, it assumes that calls to any given method of a PyMySQL connection or cursor will always have the same order. Hence:

```{warning}
This plugin is *not* thread-safe. If a given test accesses the database in a non-deterministic manner (such as by using multiple connections), it may fail.
```

An important limitation should also be pointed out:

```{warning}
This plugin currently only works the first time you connect to a SQL Alchemy database engine. You therefore have to make sure that you create a new engine for every test.
```

## Installation

You can install the plugin in the usual way with pip:

```shell
python -m pip install pytest-pymysql-snapshot-mock
```

pytest will automatically pick up the plugin.

## Using the plugin

When you run pytest after installing pytest-pymysql-snapshot-mock, you will see no change;  your real database connection is used and no data is stored.

However, this changes if you run pytest with the `--store-db-data` flag. When doing so, you also have to use the `--db-data-dir` option with the path of the directory where the database snapshot files are to be stored.

```shell
pytest --store-db-data --db-data-dir /path/to/test-db-data/
```

As an alternative to the `--db-data-dir` option you can set the environment variable `PMSM_DATA_DIR`. If both the command line option and the environment variable are defined, the value of the command line option is used.
 
Now for every test file a directory is generated, and these new directories contain data files for every test run.

```{note}
These directories and files are also created if a test doesn't use the database at all. This might be improved in a future version.
```

The generated files should be put under version control. (Remember the warning above: They contain database data. Make sure they do not contain confidential information, or that the repository for them is private.)

In order to mock the database and use the previously stored data, you need to run pytest with the `--mock-db-data` flag. Again the `--db-data-dir` option is required as well, unless the environment variable `PMSM_DATA_DIR` is set.

```shell
pytest --mock-db-data --db-data-dir /path/to/test-db-data/
```

### Handling random data

If you test with a "real" database, your tests may have to use random data. For example, consider creating users with the constraint that their username is unique in the database. If you use a fixed username, you have to delete the new user after every test run. But this is potentially brittle and more pain than gain. So you would rather generate a different, random username for each test run.

But this poses a problem for mocking. Imagine that your test is checking that the created user has the correct username. When you run the test, a new username is generated, but the mocked database data contains the previously generated username. Clearly the two differ and the test fails.

To solve this issue, pytest-pymysql-snapshot-mock offers a fixture `database_mock` with a `user_value` method. If no mocking is used, this method returns the value passed to it, and if database data is being stored, it also saves this value. However, if the database is being mocked, `user_value` ignores its argument and instead returns the previously stored value.

The following example illustrates how the `user_value` method can be used.

```python
import uuid

def test_create_user(database_mock):
    username = database_mock.user_value(str(uuid.uuid4())[:8])
    user = {
        "username": username
    }
    store_user(user)
    assert fetch_user(username) == user
```

```{warning}
When you use the `user_value` method, you have to store the database data again. Otherwise you might get an ewrror about popping from an empty list.
```
