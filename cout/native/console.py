from datetime import datetime, timezone


class ConsoleColors:
    CEND = "\33[0m"

    CBOLD = "\33[1m"
    CITALIC = "\33[3m"
    CURL = "\33[4m"
    CBLINK = "\33[5m"
    CBLINK2 = "\33[6m"
    CSELECTED = "\33[7m"

    CBLACK = "\33[30m"
    CPURPLE = "\033[95m"
    CRED = "\33[31m"
    CGREEN = "\33[32m"
    CYELLOW = "\33[33m"
    CBLUE = "\33[34m"
    CVIOLET = "\33[35m"
    CBEIGE = "\33[36m"
    CWHITE = "\33[37m"

    CBLACKBG = "\33[40m"
    CREDBG = "\33[41m"
    CGREENBG = "\33[42m"
    CYELLOWBG = "\33[43m"
    CBLUEBG = "\33[44m"
    CVIOLETBG = "\33[45m"
    CBEIGEBG = "\33[46m"
    CWHITEBG = "\33[47m"

    CGREY = "\33[90m"
    CRED2 = "\33[91m"
    CGREEN2 = "\33[92m"
    CYELLOW2 = "\33[93m"
    CBLUE2 = "\33[94m"
    CVIOLET2 = "\33[95m"
    CBEIGE2 = "\33[96m"
    CWHITE2 = "\33[97m"

    CGREYBG = "\33[100m"
    CREDBG2 = "\33[101m"
    CGREENBG2 = "\33[102m"
    CYELLOWBG2 = "\33[103m"
    CBLUEBG2 = "\33[104m"
    CVIOLETBG2 = "\33[105m"
    CBEIGEBG2 = "\33[106m"
    CWHITEBG2 = "\33[107m"

    @staticmethod
    def get_color_of_style(style_str):
        if style_str == "failure":
            return ConsoleColors.CBOLD + ConsoleColors.CRED
        elif style_str == "progress":
            return ConsoleColors.CITALIC + ConsoleColors.CBLUE2
        elif style_str == "success":
            return ConsoleColors.CBOLD + ConsoleColors.CGREEN
        elif style_str == "warning":
            return ConsoleColors.CITALIC + ConsoleColors.CYELLOW
        elif style_str == "init":
            return ConsoleColors.CBOLD + ConsoleColors.CPURPLE
        elif style_str == "notice":
            return ConsoleColors.CITALIC + ConsoleColors.CBEIGE


class ConsoleOut:
    def __init__(self, header) -> None:
        self.header = header

    def get_modified(self, style, message):
        t_stamp = datetime.now(timezone.utc).strftime("%d/%m/%Y-%H:%M:%S")
        return f"{ConsoleColors.get_color_of_style(style)}{t_stamp}[~@{self.header}] > {message}{ConsoleColors.CEND}"

    def broadcast(self, style, message):
        print(self.get_modified(style, message))
