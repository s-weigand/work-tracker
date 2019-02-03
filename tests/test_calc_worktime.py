# -*- coding: utf-8 -*-
"""
Created on Sat May 14 15:32:16 2016

@author: Sebastian Weigand
"""

import os
import datetime
import pandas as pd
from pandas.util.testing import assert_frame_equal
import pytest

from work_tracker.functions.helpfer_functions import get_abs_path  # , debug_printer, seconds_to_hm
from work_tracker.functions.calc_worktime import WorktimeCalculator
from .test_update_work_db import str_datetime
from .custom_mocks import mock_True, mock_pysftp_CnOpts

pd.options.display.width = 300
pd.options.display.max_colwidth = 50


@pytest.fixture(scope="module")
def test_data_cal():
    test_df_path = get_abs_path("../tests/test_data/calc_worktime_test_DF.csv")
    test_df = pd.DataFrame([
        {"start": str_datetime("2017-08-06 23:24:33.324733"),
         "end": str_datetime("2017-08-07 0:34:33.324733"),
         "occupation": "RemEx"},
        {"start": str_datetime("2017-08-07 18:24:33.324733"),
         "end": str_datetime("2017-08-07 18:34:33.324733"),
         "occupation": "Inno"},
        {"start": str_datetime("2017-08-08 17:14:33.324733"),
         "end": str_datetime("2017-08-08 18:24:33.324733"),
         "occupation": "Inno"},
        {"start": str_datetime("2017-08-11 17:14:33.324733"),
         "end": str_datetime("2017-08-11 18:24:33.324733"),
         "occupation": "Inno"},
        {"start": str_datetime("2017-08-12 17:14:33.324733"),
         "end": str_datetime("2017-08-12 18:24:33.324733"),
         "occupation": "Inno"}])
    test_df.to_csv(test_df_path, index=False, sep="\t")

    result = pd.DataFrame([
        {"start": str_datetime("2017-08-06 23:24:33.324733"),
         "end": str_datetime("2017-08-07 0:0:0.0"),
         "occupation": "RemEx"},
        {"start": str_datetime("2017-08-07 0:0:0.0"),
         "end": str_datetime("2017-08-07 0:34:33.324733"),
         "occupation": "RemEx"},
        {"start": str_datetime("2017-08-07 18:24:33.324733"),
         "end": str_datetime("2017-08-07 18:34:33.324733"),
         "occupation": "Inno"},
        {"start": str_datetime("2017-08-08 17:14:33.324733"),
         "end": str_datetime("2017-08-08 18:24:33.324733"),
         "occupation": "Inno"},
        {"start": str_datetime("2017-08-11 17:14:33.324733"),
         "end": str_datetime("2017-08-11 18:24:33.324733"),
         "occupation": "Inno"},
        {"start": str_datetime("2017-08-12 17:14:33.324733"),
         "end": str_datetime("2017-08-12 18:24:33.324733"),
         "occupation": "Inno"}])
    manual_df_path = get_abs_path("../tests/test_data/calc_worktime_manual_df_test.csv")
    manual_df = pd.read_csv(manual_df_path,
                            parse_dates=["start", "end"], sep="\t")
    yield {"result": result,
           "test_df": test_df,
           "test_df_path": test_df_path,
           "manual_df": manual_df}
    # file_cleanup
    if os.path.isfile(test_df_path):
        os.remove(test_df_path)


@pytest.fixture(scope="function")
def Calculator(monkeypatch, test_data_cal):
    monkeypatch.setattr('work_tracker.functions.base_classes.DbBaseClass.get_remote_db',
                        mock_True)
    monkeypatch.setattr('work_tracker.functions.base_classes.DbBaseClass.push_remote_db',
                        mock_True)
    monkeypatch.setattr('pysftp.CnOpts', mock_pysftp_CnOpts)
    Calculator = WorktimeCalculator("../tests/test_data/test_user_config_calc_worktime.ini")
    # needed for all tests involving holidays
    Calculator.holidays.update({datetime.datetime(2017, 8, 4): "test_holiday"})
    return Calculator


def test_split_date_overlap_session(Calculator, test_data_cal):
    Calculator.split_date_overlap_session()
    assert_frame_equal(test_data_cal["result"], Calculator.db)


def test_get_holiday_df(Calculator):
    holidays_df = Calculator.get_holiday_df()
    holiday_result = pd.DataFrame([{"start": str_datetime("2017-08-04 0:0:0.0"),
                                    "end": str_datetime("2017-08-04 0:0:0.0"),
                                    "occupation": "holiday",
                                    "worktime": pd.to_timedelta(8, unit="h")}])
    assert_frame_equal(holidays_df, holiday_result[["start", "end", "occupation", "worktime"]])


def test_get_manual_df_with_workime(Calculator, test_data_cal):
    manual_df = Calculator.get_manual_df_with_workime()
    test_data_cal["manual_df"].loc[:, "worktime"] = \
        pd.to_timedelta(test_data_cal["manual_df"]["worktime"], unit="h")
    assert_frame_equal(manual_df, test_data_cal["manual_df"])


def test_init_holidays(Calculator):
    assert (datetime.datetime(2017, 1, 1) in Calculator.holidays), \
        "german default holiday not in holidays"
    assert (datetime.datetime(2017, 12, 24) in Calculator.holidays), \
        "special holiday not in holidays"

    Calculator.country = "US"
    Calculator.province = ""
    Calculator.holidays = Calculator.init_holidays()
    assert (datetime.datetime(2015, 7, 4) in Calculator.holidays), \
        "US default holiday not in holidays"


def test_get_daily_worktime(Calculator):
    weekly_40h = Calculator.get_daily_worktime("weekly", 40, "Mon Tue Wed Thu Fri")
    assert weekly_40h == 8.0
    # this work time and weekmask were chosen, so daily work would be exactly 1
    monthly_8_75h = Calculator.get_daily_worktime("monthly", 8.75, "Thu Fri")
    assert monthly_8_75h == 1


def test_generate_contract_worktime_df(Calculator):
    contact_worktime_df = Calculator.generate_contract_worktime_df()
    date_index = pd.date_range("2017-08-04", "2017-08-11", normalize=True)
    result_df = pd.DataFrame({"worktime": pd.to_timedelta([8]*7+[1], unit="h"),
                              "start": pd.Series(date_index)})
    # drop rows not in test week mask
    result_df.drop([1, 2], inplace=True)
    result_df.reset_index(drop=True, inplace=True)
    # debug_printer(result_df)
    # debug_printer(contact_worktime_df)
    assert_frame_equal(contact_worktime_df, result_df[['start', 'worktime']])


def test_get_total_df(Calculator):
    total_df = Calculator.get_total_df()

    result_path = get_abs_path("../tests/test_data/calc_worktime_total_df_test.csv")
    result_df = pd.read_csv(result_path,
                            parse_dates=["start", "end"], sep="\t",
                            converters={"worktime": pd.to_timedelta})
    assert_frame_equal(total_df, result_df)


def test_get_plot_df(Calculator):
    plot_df = Calculator.get_plot_df()
    plot_df.reset_index(inplace=True)
    result_path = get_abs_path("../tests/test_data/calc_worktime_plot_df_test.csv")
    result = pd.read_csv(result_path, sep="\t", parse_dates=["start"],
                         converters={'Inno': pd.to_timedelta,
                                     'RemEx': pd.to_timedelta,
                                     'holiday': pd.to_timedelta,
                                     'sick': pd.to_timedelta,
                                     'total': pd.to_timedelta,
                                     'vacation': pd.to_timedelta})
    assert_frame_equal(plot_df, result)
