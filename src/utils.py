"""
## utils.py

Define various utility functions.
"""

import os
import sys


def construct_img_path(
    project_dir: str, topic_name: str, file_type: str, file_name: str
):
    """
    Construct the path to store the image
    """
    assert file_type in [
        "ann",
        "img",
        "meta",
    ], "file type should be one of ['ann', 'img', 'meta']"

    topic_name = topic_name.strip("/").replace("/", "-")
    return os.path.join(project_dir, topic_name, file_type, file_name)


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
