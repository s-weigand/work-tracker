"""
@file: test_helper_functions.py
@author: Sebastian Weigand
"""

import datetime
import os

from work_tracker.functions.helpfer_functions import (
    debug_printer,
    get_abs_path,
    get_midnight_datetime,
    seconds_to_hm,
    str_datetime,
)


def test_str_datetime():
    date = datetime.datetime(2017, 8, 9, 18, 24, 33, 324733)
    date_str = "2017-08-09 18:24:33.324733"
    assert date == str_datetime(date_str)


def test_get_midnight_datetime():
    date = datetime.datetime(2017, 8, 9, 18, 24, 33, 324733)
    midnight_date = datetime.datetime(2017, 8, 9, 0, 0, 0, 0)
    assert midnight_date == get_midnight_datetime(date)


def test_get_abs_path():
    abs_path = get_abs_path("")
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../work_tracker"))
    assert os.path.isabs(abs_path)
    # looks strange but with the drive letter being capital or
    # not this caused problems ...
    assert os.path.relpath(abs_path, base_path) == "."


def test_seconds_to_hm():
    seconds = 3600 + 120 + 11
    assert seconds_to_hm(seconds) == "1:02"


def test_debug_printer(capsys):
    testvar = "testvar content"
    debug_printer(testvar)
    captured = capsys.readouterr()
    assert (
        captured.out
        == """
##################################################
testvar
##################################################

testvar content
"""
    )
