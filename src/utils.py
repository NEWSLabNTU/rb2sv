"""
## utils.py

Define various utility functions.
"""

import os


def construct_file_path(
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
