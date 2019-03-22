#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
"""Manages Command Line Interface arguments"""

import sys
import argcomplete
import argparse

# custom modules
import globals


def get_cli_args():
    """Retrieves Command Line Interface arguments"""

    parser = argparse.ArgumentParser()  # initializing parser object

    parser.add_argument("--server")
    parser.add_argument("--user", choices=globals.USERS, required=True)
    parser.add_argument("--microservice", nargs='*', choices=globals.APPS, required=True)
    parser.add_argument("--healthcheck", action='store_true')  # store_true means no value needed

    if len(sys.argv) < 2:  # if only script name provided, without args

        parser.print_usage()
        sys.exit(1)

    argcomplete.autocomplete(parser)  # autocomplete
    args = parser.parse_args()

    if not (args.microservice):
        parser.error('Please choose at least one --microservice to deploy')

    return(args)
