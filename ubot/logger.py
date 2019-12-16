from time import strftime
import threading


RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
GREY = "\033[90m"
BLACK = "\033[90m"
DEFAULT = "\033[99m"

ANSI_RESET = "\u001B[0m"
ANSI_BLACK = "\u001B[30m"
ANSI_RED = "\u001B[31m"
ANSI_GREEN = "\u001B[32m"
ANSI_YELLOW = "\u001B[33m"
ANSI_BLUE = "\u001B[34m"
ANSI_PURPLE = "\u001B[35m"
ANSI_CYAN = "\u001B[36m"
ANSI_WHITE = "\u001B[37m"

END_TAB = "\033[0m"

CLR_MSG = BLUE
CLR_SUCCESS = GREEN
CLR_WARNING = YELLOW
CLR_ERROR = RED
CLR_INFO = ANSI_PURPLE


def _on_main_thread():
    return threading.current_thread().name == "MainThread"


def _format(text):
    """
    Method to add a timestamp to a log message

    Args:
        text (string): log message

    Returns:
        string - log message with timestamp appended
    """
    if not _on_main_thread():
        thread_name = threading.current_thread().name
        return "[{}]@{}: {}".format(strftime("%Y-%m-%d %H:%M:%S"), thread_name, text)

    return "[{}] {}".format(strftime("%Y-%m-%d %H:%M:%S"), text)


def _print(text, *args, color=None):
    """
    Print text to standard output with color
    """
    if len(args) > 0:
        text = (text or "").format(*args)

    text = _format(text or "")

    if color is None:
        print(text)
    else:
        print(f"{color}{text}{END_TAB}")


def message(text, *args):
    """
    Method to print a log message to the console, with the 'text' colors

    Args:
        text (string): log message
    """
    _print(text, *args, color=CLR_MSG)


def success(text, *args):
    """
    Method to print a log message to the console, with the 'success'
    colors

    Args:
        text (string): log message
    """
    _print(text, *args, color=CLR_SUCCESS)


def warning(text, *args):
    """
    Method to print a log message to the console, with the 'warning'
    colors

    Args:
        text (string): log message
    """
    _print(text, *args, color=CLR_WARNING)


def error(text, *args):
    """Method to print a log message to the console, with the 'error'
    colors

    Args:
        text (string): log text
    """
    _print(text, *args, color=CLR_ERROR)


def info(text, *args):
    """Method to print a log message to the console, with the 'info'
    colors

    Args:
        text (string): log text
    """
    _print(text, *args, color=CLR_INFO)


def debug(text, *args, debug=True, thread_debug=True):
    """Method to print a debug message to the console, with the 'text'
    colors

    Args:
        text (string): log text
    """
    if not debug:
        return

    if not _on_main_thread() and not thread_debug:
        return

    _print(text, *args)
