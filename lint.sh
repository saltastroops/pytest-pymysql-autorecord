black src tests && \
isort src tests && \
flake8 src tests && \
mypy src && \
pytest && \
tox -e docs
