"""
## utils.py

Define various utility functions.
"""

import os
import sys
import random

from error import InvalidConfigError


def is_yaml_file(p: str):
    if p.endswith(".yaml"):
        return p
    raise InvalidConfigError(f"Config file should be in yaml format")


def parse_topic_name(t: str) -> str:
    return t.strip("/").replace("/", "-")


def prompt_confirm(default=True):
    """
    Prompt the user to continue the process or quit.
    """
    while True:
        ans = (
            input("Continue? ([Y]/n)")
            if default is True
            else input("Continue? (y/[N])")
        )
        if ans == "":
            if default is True:
                return
            else:
                sys.exit(0)

        if ans in ("y", "Y"):
            return
        elif ans in ("n", "N"):
            sys.exit(0)
        else:
            print("Invlaid input. Enter 'y' to continue or 'n' to quit.")


def scientific_to_decimal(s: str) -> str:
    return "{:.35f}".format(float(s)).rstrip("0").rstrip(".")


def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))
