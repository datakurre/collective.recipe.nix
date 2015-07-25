# -*- coding: utf-8 -*-
from configparser import ConfigParser
import contextlib
import os


FILENAME = 'collective.recipe.nix.cfg'
PATHS = [
    os.path.expanduser('~/.{0:s}'.format(FILENAME)),
    '.{0:s}'.format(FILENAME),
    FILENAME,
]


def filename():
    for path in PATHS:
        if os.path.isfile(path):
            return path
    return '.{0:s}'.format(FILENAME)


def load():
    config = ConfigParser()
    config.read(PATHS)
    if not config.has_section('urls'):
        config.add_section('urls')
    return config


def save(config):
    with open(filename(), 'w') as fp:
        config.write(fp)


@contextlib.contextmanager
def edit():
    config = load()
    try:
        yield config
    finally:
        save(config)


def with_cache(func):
    def wrapper(*args, **kwargs):
        with edit() as config:
            kwargs['cache'] = config
            return func(*args, **kwargs)
    return wrapper
