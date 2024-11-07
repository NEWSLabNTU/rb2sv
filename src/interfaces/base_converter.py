class BaseConverter:
    def __init__(self, args) -> None:
        self.args = args

    def log(self, *args, **kargs):
        if not self.args.quiet:
            print(*args, **kargs)
