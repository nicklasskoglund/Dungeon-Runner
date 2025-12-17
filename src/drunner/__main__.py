# src/drunner/__main__.py

'''
Module entry point for the drunner package.

This file enables running the package as a script, e.g.:
    python -m drunner

It delegates execution to the CLI layer (drunner.cli.main).
'''

from drunner.cli import main

if __name__ == '__main__':
    # Convert the returned exit code into a proper process exit status.
    raise SystemExit(main())