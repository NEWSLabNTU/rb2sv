from config import Rb2svConfig


class BaseConverter:
    def __init__(self, args: Rb2svConfig) -> None:
        self.args = args

    def log(self, *args, **kargs):
        if not self.args.quiet:
            print(*args, **kargs)
