"""
@file: test_update_work_db.py
@author: Sebastian Weigand
"""

import datetime

# import numpy as np
import pandas as pd
import pytest
from pandas.util.testing import assert_frame_equal
from tests.custom_mocks import (
    mock_datetime_now,
    mock_datetime_now_date_change,
    mock_numpy_now_date_change,
    mock_pysftp_CnOpts,
    mock_time_long_break,
    mock_time_short_break,
    mock_True,
    mock_var_time,
)

from work_tracker.functions.helpfer_functions import get_midnight_datetime, str_datetime
from work_tracker.functions.update_work_db import DbInteraction


@pytest.fixture(scope="function")
def DbInteraction_worker(test_data_base, monkeypatch):
    monkeypatch.setattr("work_tracker.functions.base_classes.DbBaseClass.get_remote_db", mock_True)
    monkeypatch.setattr(
        "work_tracker.functions.base_classes.DbBaseClass.push_remote_db", mock_True
    )
    monkeypatch.setattr("pysftp.CnOpts", mock_pysftp_CnOpts)
    DbInteraction_worker = DbInteraction("../tests/test_data/test_user_config_update_work_db.ini")
    # mocking the today value
    DbInteraction_worker.today = datetime.datetime(2017, 8, 8, 0, 0, 0, 0)
    DbInteraction_worker.tomorrow = datetime.datetime(2017, 8, 9, 0, 0, 0, 0)
    return DbInteraction_worker


def test_get_session_time(DbInteraction_worker):
    assert DbInteraction_worker.get_session_time() == "1:10"


def test_update_now_and_tomorrow(DbInteraction_worker, monkeypatch):
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_datetime_now",
        mock_datetime_now,
    )
    DbInteraction_worker.update_now_and_tomorrow()
    assert DbInteraction_worker.today == get_midnight_datetime(
        str_datetime("2017-08-08 18:29:33.0")
    )
    assert DbInteraction_worker.tomorrow == get_midnight_datetime(
        str_datetime("2017-08-08 18:29:33.0")
    ) + datetime.timedelta(1)


def test_update_db_locale_short_break(DbInteraction_worker, monkeypatch):
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_pandas_now",
        mock_time_short_break,
    )
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_datetime_now",
        mock_datetime_now,
    )
    session_time = DbInteraction_worker.update_db_locale()
    assert session_time == ("17:14", "1:15")
    assert len(DbInteraction_worker.db.index) == 3


def test_update_db_locale_long_break(DbInteraction_worker, monkeypatch):
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_pandas_now",
        mock_time_long_break,
    )
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_datetime_now",
        mock_datetime_now,
    )
    session_time = DbInteraction_worker.update_db_locale()
    assert session_time == ("17:14", "1:10")
    assert len(DbInteraction_worker.db.index) == 4


def test_update_db_with_day_change_and_running_update(DbInteraction_worker, monkeypatch):
    # this is due to a bug i observed, where after midnight new rows did get appended
    # with start midnight and end current time
    db_before = DbInteraction_worker.db.copy()
    for offset in range(10):
        monkeypatch.setattr(
            "work_tracker.functions.update_work_db.DbInteraction.get_pandas_now",
            mock_var_time(offset * 2),
        )
        monkeypatch.setattr(
            "work_tracker.functions.update_work_db.DbInteraction.get_datetime_now",
            mock_var_time(offset * 2, kind="datetime"),
        )
        session_time = DbInteraction_worker.update_db_locale()

    new_row = pd.DataFrame(
        [
            {
                "start": str_datetime("2017-08-08 23:59:00.0"),
                "end": str_datetime("2017-08-09 00:00:00.0"),
                "occupation": "TestOccupation1",
            },
            {
                "start": str_datetime("2017-08-09 00:00:00.0"),
                "end": str_datetime("2017-08-09 00:17:00.0"),
                "occupation": "TestOccupation1",
            },
        ]
    )
    result = db_before.append(new_row, ignore_index=True, sort=False)
    assert session_time == ("0:00", "0:17")  # type:ignore
    assert len(DbInteraction_worker.db.index) == 5
    assert_frame_equal(DbInteraction_worker.db, result)


def test_update_db_date_changed_during_session_short_break(DbInteraction_worker, monkeypatch):
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_pandas_now",
        mock_numpy_now_date_change,
    )
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_datetime_now",
        mock_datetime_now_date_change,
    )
    new_row = pd.DataFrame(
        [
            {
                "start": str_datetime("2017-08-08 20:39:33.0"),
                "end": str_datetime("2017-08-08 23:57:33.0"),
                "occupation": "TestOccupation",
            }
        ]
    )
    DbInteraction_worker.db = DbInteraction_worker.db.append(new_row, sort=False)
    session_time = DbInteraction_worker.update_db_locale()
    assert session_time == ("0:00", "0:05")
    assert len(DbInteraction_worker.db.index) == 5


def test_update_db_date_changed_during_session_long_break(DbInteraction_worker, monkeypatch):
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_pandas_now",
        mock_numpy_now_date_change,
    )
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_datetime_now",
        mock_datetime_now_date_change,
    )
    new_row = pd.DataFrame(
        [
            {
                "start": str_datetime("2017-08-08 20:39:33.0"),
                "end": str_datetime("2017-08-08 23:37:33.0"),
                "occupation": "TestOccupation",
            }
        ]
    )
    DbInteraction_worker.db = DbInteraction_worker.db.append(new_row, sort=False)
    session_time = DbInteraction_worker.update_db_locale()
    assert session_time == ("0:05", "0:00")
    assert len(DbInteraction_worker.db.index) == 5


def test_get_start_time(DbInteraction_worker):
    start_time = DbInteraction_worker.get_start_time()
    assert start_time == "17:14"


def test_start_session_short_break(DbInteraction_worker, monkeypatch, test_data_base):
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_pandas_now",
        mock_time_short_break,
    )
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_datetime_now",
        mock_datetime_now,
    )
    DbInteraction_worker.start_session()
    result = test_data_base["result"].copy()
    result.at[2, "end"] = mock_time_short_break()
    assert_frame_equal(DbInteraction_worker.db, result)


def test_start_session_long_break(DbInteraction_worker, monkeypatch, test_data_base):
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_pandas_now",
        mock_time_long_break,
    )
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_datetime_now",
        mock_datetime_now,
    )
    new_row = pd.DataFrame(
        [
            {
                "start": str_datetime("2017-08-08 18:39:33.0"),
                "end": str_datetime("2017-08-08 18:39:33.0"),
                "occupation": "TestOccupation",
            }
        ]
    )
    result = test_data_base["result"].copy().append(new_row, ignore_index=True, sort=False)
    result.sort_values("start").reset_index(drop=True, inplace=True)
    DbInteraction_worker.occupation = "TestOccupation"
    DbInteraction_worker.start_session()
    assert_frame_equal(DbInteraction_worker.db, result)


def test_change_occupation(DbInteraction_worker, monkeypatch):
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_pandas_now",
        mock_time_short_break,
    )
    monkeypatch.setattr(
        "work_tracker.functions.update_work_db.DbInteraction.get_datetime_now",
        mock_datetime_now,
    )
    DbInteraction_worker.update_db_locale()
    new_db = DbInteraction_worker.db.copy()
    new_day_df = pd.DataFrame(
        [
            {
                "start": mock_time_short_break(),
                "end": mock_time_short_break(),
                "occupation": "RemEx",
            }
        ]
    )
    new_db = new_db.append(new_day_df, ignore_index=True, sort=False)
    DbInteraction_worker.change_occupation("RemEx")
    assert_frame_equal(DbInteraction_worker.db, new_db)
