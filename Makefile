APP_DIR_NAME = app


# make run: run an application.
.PHONY: run
run:
	pipenv run python -m $(APP_DIR_NAME)

# make test: run tests.
.PHONY: test
test:
	pipenv run pytest $(APP_DIR_NAME)

# make report: run tests and generate coverage report.
.PHONY: report
report:
	pipenv run pytest --cov-config=.coveragerc --cov=$(APP_DIR_NAME)

# make install: install what's needed.
.PHONY: install
install:
	pip install pipenv; \
	pipenv install; \
	pipenv install --dev
