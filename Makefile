APP_DIR_NAME = app


# make run: run an application.
.PHONY: run
run:
	pipenv run python -m $(APP_DIR_NAME)

# make test: run tests.
.PHONY: test
test:
	pipenv run pytest $(APP_DIR_NAME)

# make install: install what's needed.
.PHONY: install
install:
	pip install pipenv; \
	pipenv install; \
	pipenv install --dev
