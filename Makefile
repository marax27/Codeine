APP_DIR_NAME = app


# make run: run an application.
.PHONY: run
run:
	pipenv run python -m $(APP_DIR_NAME)

# make test: run tests.
.PHONY: test
test:
	pipenv run pytest $(APP_DIR_NAME)
