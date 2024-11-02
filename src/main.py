import sys
import argparse

from utils import is_yaml_file

if __name__ == "__main__":
    # Test the module import
    try:
        from rb2sv import Rb2sv
    except ImportError as err:
        print(err)
        print(
            """\n
HINT: If the modules couldn't be imported are ros2-related,
the reason might be that you forgot to source ros2's setup.bash.
"""
        )
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="No logging during conversion"
    )
    parser.add_argument(
        "-c",
        "--config-file-path",
        required=True,
        type=is_yaml_file,
        help="Tool configuration yaml file",
    )
    args = parser.parse_args()

    r = Rb2sv(args)
    r.read_into_project()
    sys.exit(0)
