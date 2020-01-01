# Codeine

![Travis (.org)](https://img.shields.io/travis/marax27/Codeine)
![Coveralls github branch](https://img.shields.io/coveralls/github/marax27/Codeine/master)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

![GitHub issues](https://img.shields.io/github/issues-raw/marax27/Codeine)
![GitHub closed issues](https://img.shields.io/github/issues-closed-raw/marax27/Codeine)
![GitHub pull requests](https://img.shields.io/github/issues-pr/marax27/Codeine)

Computing over Decentralized Network, with P2P

## Getting Started

0. Install necessary software such as Python3 or Make.
1. Clone the repository.
2. `make install`.
3. (optional) Setup Visual Studio Code to work with Python
    1. Install official *Python* extension.
    2. Enable linting (`Ctrl+Shift+P` → *Enable Linting*)
    3. ~~Select *pycodestyle* as a linter (`Ctrl+Shift+P` → *Select Linter*)~~ You'll want 2 linters to be enabled: *pylint* (error detection) and *pycodestyle* (code style hints). To achieve that, make sure these 2 options are set in .vscode/settings.json: `"python.linting.pylintEnabled = true"`, `"python.linting.pycodestyleEnabled = true"`.

### Run an application
Use `make run`.

### Test an application
Use `make test` to run unit tests. `make report` additionally generates a code coverage report.

