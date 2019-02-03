# -*- coding: utf-8 -*-
"""
@file: helperfunctions.py
@author: Sebastian Weigand
"""
import os
import datetime
import inspect
import re


def get_abs_path(rel_path):
    """
    Helperfunction to get the absolute path in respect to the main file ("work_tracker.pyw")

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
    return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", rel_path))


def str_datetime(time_str):
    """
    Converts a string in Datetime64[ns] format to a datetime object

    Parameters
    ----------
    time_str: str
        string representing the datetime

    Returns
    -------
        time: datetime
            datetime which was represented by time_str
    """
    return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")


def get_midnight_datetime(datetime_obj):
    """
    Helperfunction to get the date at exactly midnight for a given datime object

    Parameters
    ----------
    datetime_obj : datetime.datetime
        datetime object containing a date

    Returns
    -------
    datetime object set to exactly midnight : datetime.datetime
        String representing the seconds which where passed as %h:%M
    """
    return datetime_obj.replace(minute=0, hour=0, second=0, microsecond=0)


def seconds_to_hm(seconds):
    """
    Helperfunction to convert Number of seconds passed to a more human readable %h:%M string format

    Parameters
    ----------
    seconds : int
        Amount of seconds that should be converted to an %h:%M string

    Returns
    -------
    %h:%M representation of the seconds : str
        String representing the seconds which where passed as %h:%M
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d" % (h, m)


def debug_printer(arg):
    """
    Convenience function to print variables in a matter that they are easily seen
    and their name as well as their value is printed

    Parameters
    ----------
    arg : anything
    """
    frame = inspect.currentframe()
    try:
        context = inspect.getframeinfo(frame.f_back).code_context
        caller_lines = ''.join([line.strip() for line in context])
        m = re.search(r'debug_printer\s*\((.+)\)$', caller_lines)
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
