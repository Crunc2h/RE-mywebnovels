import cout.native.console as cout


class NovelProcessException(Exception):
    def __init__(self, message) -> None:
        self.message = cout.ConsoleOut.get_modified(style="failure", message=message)
        super().__init__(self.message)


class ProcessLaunchException(NovelProcessException):
    pass


class ProcessSpiderException(NovelProcessException):
    pass


class ProcessInternalException(NovelProcessException):
    pass
