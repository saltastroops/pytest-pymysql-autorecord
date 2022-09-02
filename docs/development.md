# Development

## Developing the package

If you want to work on pytest-pymysql-autorecord, you should first clone its repository.

Afterwards, change into the cloned directory, create and activate a virtual environment, and install the required Python libraries.

```shell
cd /path/to/dir
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

For linting during development you can use the script `lint.sh`.

```shell
./lint.sh
```

To check the code before pushing it to the repository you can use the script `check.sh`.

## Publishing the package

### Publishing manually

In order to publish pytest-pymysql-autorecord from your machine, first install twine, if you haven't done so already:

```shell
pipx install twine
```

Then remove the `dist` folder if need be:

```shell
rm -r dist
```

Build the package:

```shell
pyproject-build --sdist
```

If you have your own PyPI server, say `https://pypi.example.com`, create a file `.pypirc` in your home directory with the following content:

```
[distutils]
index-servers =
pypi
testpypi
example

[pypi]
repository = https://upload.pypi.org/legacy/

[testpypi]
repository = https://test.pypi.org/legacy/

[example]
repository = https://pypi.example.com/
```

You can then use twine to upload the package:

```shell
twine upload -r https://pypi.example.com dist/*
```

Afterwards you can install pytest-pymysql-autorecord from your PyPI server with

```shell
python -m pip install --index-url https://pypi.example.com/
```

Upload the package to [Test PyPI](https://packaging.python.org/guides/using-testpypi/):

```shell
twine upload -r testpypi dist/*
```

You can then install pytest-pymysql-autorecord from Test PyPI with

```shell
python -m pip install --extra-index-url https://test.pypi.org/simple/ pytest-pymysql-autorecord
```

```{warning}
TestPyPI lets you copy a command for installing the package. However, this uses `--index-url` instead of `--extra-index-url` and gives an error because setuptools cannot be found on TestPyPI.
```

If all looks good, you can publish your package:

```shell
twine upload dist/*
```
