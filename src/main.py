import sys

if __name__ == "__main__":
    # Test the module import
    try:
        from rb2sv import Rb2sv
    except ImportError as err:
        print(err)
        print(
            "\nHINT: If the modules couldn't be imported are ros2-related, \
the reason might be that you forgot to source ros2's setup.bash."
        )
        sys.exit(1)

    r = Rb2sv()
    r.read_into_project()
    sys.exit(0)
