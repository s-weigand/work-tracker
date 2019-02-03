# -*- coding: utf-8 -*-
"""
@file: test_update_work_db.py
@author: Sebastian Weigand
"""

import pandas as pd
from datetime import datetime

from work_tracker.functions.helpfer_functions import str_datetime


def mock_time_short_break(*args):
    return pd.to_datetime("2017-08-08 18:29:33")  # 5min


def mock_time_long_break(*args):
    return pd.to_datetime("2017-08-08 18:39:33.0")  # 15min


def mock_datetime_now(*args):
    return str_datetime("2017-08-08 18:29:33.0")


class mockDatetimeNow(datetime):
    nanosecond = 0

    @classmethod
    def now(cls, tz=None):
        return str_datetime("2017-08-08 18:29:33.000000")


def mock_datetime_now_date_change(*args):
    return str_datetime("2017-08-09 00:05:00.0")


def mock_numpy_now_date_change(*args):
    return pd.to_datetime("2017-08-09 00:05:00.0")


def mock_True(*args):
    return True


def mock_False(*args):
    return False


def mock_void(*args):
    pass


def mock_pysftp_CnOpts():
    class CnOptsMockClass:
        def __init__(self):
            self.hostkeys = None
    return CnOptsMockClass
