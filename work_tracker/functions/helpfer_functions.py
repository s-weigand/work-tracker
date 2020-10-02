"""Module containing helper functions."""
import datetime
import hashlib
import inspect
import os
import re
from typing import Union
from warnings import warn


def get_abs_path(rel_path):
    """
    Helperfunction to get the absolute path in respect to the main file ("work_tracker.pyw").

    Parameters
    ----------
    rel_path : str
        relative path to a file

    Returns
    -------
    absolute path : str
        absolute path evaluated from the relative path in respect to
        the path of the main file("work_tracker.pyw")
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", rel_path))


def str_datetime(time_str: str):
    """
    Convert a string in Datetime64[ns] format to a datetime object.

    Parameters
    ----------
    time_str: str
        string representing the datetime

    Returns
    -------
    datetime
        datetime which was represented by time_str
    """
    return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")


def get_midnight_datetime(datetime_obj: datetime.datetime):
    """
    Helperfunction to get the date at exactly midnight for a given datetime object.

    Parameters
    ----------
    datetime.datetime
        datetime object containing a date

    Returns
    -------
    datetime.datetime
        String representing the seconds which where passed as %h:%M
    """
    return datetime_obj.replace(minute=0, hour=0, second=0, microsecond=0)


def seconds_to_hm(seconds: int) -> str:
    """
    Helperfunction to convert Number of seconds to hour:minute format.

    Parameters
    ----------
    seconds : int
        Amount of seconds that should be converted to an %h:%M string

    Returns
    -------
    str
        String representing of seconds, in the form of %h:%M
    """
    m, _ = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d" % (h, m)


def hash_file(file_path: str) -> Union[str, None]:
    """
    Calculate the md5 hash value of the file at file_path.

    Parameters
    ----------
    file_path : str
        Path to the file that should be hashed.

    Returns
    -------
    str
        MD5 hex  hash value of the file at file_path.
    """
    if os.path.isfile(file_path):
        with open(file_path, "rb") as file:
            hash_val = hashlib.md5(file.read())
        return hash_val.hexdigest()
    else:
        warn(UserWarning(f"The file {file_path} does not exist."))


def debug_printer(arg):
    """
    Print variable names and their values.

    Convenience function to print variables in a matter that they are easily seen
    and their name as well as their value is printed.

    Parameters
    ----------
    arg : anything
    """
    frame = inspect.currentframe()
    try:
        context = inspect.getframeinfo(frame.f_back).code_context  # type: ignore
        caller_lines = "".join([line.strip() for line in context])
        m = re.search(r"debug_printer\s*\((.+)\)$", caller_lines)
        if m:
            caller_lines = m.group(1)
        padding = 50
        print()
        print("#" * padding)
        print(caller_lines)
        print("#" * padding)
        print()
        print(arg)
    finally:
        del frame


if __name__ == "__main__":
    test_var = "HUHU"
    debug_printer(test_var)
