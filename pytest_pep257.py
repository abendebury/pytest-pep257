"""PEP257 plugin for pytest.

py.test plugin that the uses PEP 257 docstring style checker
(https://github.com/GreenSteam/pep257/) to report compliance with Python
PEP 257 (http://www.python.org/dev/peps/pep-0257).
"""
import pytest
import pep257


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption('--pep257',
                    action='store_true',
                    help="perform pep257 compliance on .py files")


def pytest_collect_file(parent, path):
    config = parent.config
    if config.option.pep257 and file_should_be_checked(path):
        config._pep257ignore = config.getini("pep257ignore")
        return Pep257Item(path, parent)


def file_should_be_checked(path):
    return path.ext == ".py" and not path.basename.startswith("test")


class Pep257Item(pytest.Item, pytest.File):
    def __init__(self, path, parent, ignored):
        super(Pep257Item, self).__init__(path, parent)
        self.ignored = ignored or None

    def runtest(self):
        check_result = pep257.check([str(self.fspath)], ignore=self.ignored)
        errors = [str(error) for error in check_result]
        if errors:
            raise PEP257Error("\n".join(errors))

    def repr_failure(self, excinfo):
        if excinfo.errisinstance(PEP257Error):
            return excinfo.value.args[0]
        return super(Pep257Item, self).repr_failure(excinfo)

    def reportinfo(self):
        return (self.fspath, -1, "PEP257-check")


class PEP257Error(Exception):
    """Indicate error due to pep257 checks."""
