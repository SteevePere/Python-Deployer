#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
"""Manages Command Line Interface arguments"""

import sys
import argcomplete, argparse

import globals


def get_cli_args():
    """Retrieves Command Line Interface arguments"""

    parser = argparse.ArgumentParser()

    parser.add_argument("--server")
    parser.add_argument("--user", choices = globals.USERS, required=True)
    parser.add_argument("--microservice", nargs='*', choices = globals.APPS, required=True)
    parser.add_argument("--healthcheck", action='store_true')

    if len(sys.argv) < 2:

        parser.print_usage()
        sys.exit(1)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if not (args.microservice):
        parser.error('Please choose at least one --microservice to deploy')

    return(args)
