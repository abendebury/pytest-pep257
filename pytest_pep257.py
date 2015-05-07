"""PEP257 plugin for pytest.

py.test plugin that the uses PEP 257 docstring style checker
(https://github.com/GreenSteam/pep257/) to report compliance with Python
PEP 257 (http://www.python.org/dev/peps/pep-0257).
"""
import os
import re

import pep257
import pytest


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption('--pep257',
                    action='store_true',
                    help="perform pep257 compliance on .py files")
    parser.addini('pep257ignore', type='linelist',
        help='Each line specifies a glob pattern and whitespace '
             'separated PEP257 errors and warnings that will be ignored, '
             'example: *.py D203')


def pytest_collect_file(parent, path):
    config = parent.config
    ignore = Ignorer(config.getini('pep257ignore'))(path)
    if config.option.pep257 and file_should_be_checked(path) and \
            ignore is not None:
        return Pep257Item(path, parent, ignore)


def file_should_be_checked(path):
    return path.ext == ".py" and not path.basename.startswith("test")


class Pep257Item(pytest.Item, pytest.File):
    def __init__(self, path, parent, ignore):
        super(Pep257Item, self).__init__(path, parent)
        self.ignore = ignore

    def runtest(self):
        errors = [str(error) for error in pep257.check([str(self.fspath)],
                                                       self.ignore)]
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


class Ignorer:
    """Based on Pytest-PEP8 ignorer."""

    def __init__(self, ignorelines, coderex=re.compile('D\d\d\d')):
        self.ignores = ignores = []
        for line in ignorelines:
            i = line.find('#')
            if i != -1:
                line = line[:1]
            try:
                glob, ign = line.split(None, 1)
            except ValueError:
                glob, ign = None, line
            if glob and coderex.match(glob):
                glob, ign = None, line
            ign = ign.split()
            if "ALL" in ign:
                ign = None
            if glob and "/" != os.sep and "/" in glob:
                glob = glob.replace("/", os.sep)
            ignores.append((glob, ign))

    def __call__(self, path):
        l = []
        for (glob, ignlist) in self.ignores:
            if not glob or path.fnmatch(glob):
                if ignlist is None:
                    return None
                l.extend(ignlist)
        return l
