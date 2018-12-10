# -*- coding: utf-8 -*-
"""
@file: test_update_work_db.py
@author: Sebastian Weigand
"""

import os
import datetime
import pytest
import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal

from work_tracker.functions.helpfer_functions import get_abs_path, get_midnight_datetime
from work_tracker.functions.base_classes import DbBaseClass
from tests.test_mocks import *


@pytest.fixture(scope="function")
def test_data():
    offline_df_path = get_abs_path("../tests/test_data/test_DF_offline.csv")
    online_df_path = get_abs_path("../tests/test_data/test_DF_online.csv")
    offline_df = pd.DataFrame([{"start": str_datetime("2017-08-06 18:24:33.324733"),
                                "end": str_datetime("2017-08-06 18:34:33.324733"),
                                "occupation": "RemEx"},
                               {"start": str_datetime("2017-08-07 18:24:33.324733"),
                                "end": str_datetime("2017-08-07 18:34:33.324733"),
                                "occupation": "Inno"},
                               {"start": str_datetime("2017-08-08 17:14:33.324733"),
                                "end": str_datetime("2017-08-08 18:24:33.324733"),
                                "occupation": "Inno"}])
    offline_df.to_csv(offline_df_path, index=False, sep="\t")

    online_df = pd.DataFrame([{"start": str_datetime("2017-08-06 18:24:33.324733"),
                               "end": str_datetime("2017-08-06 18:44:33.324733"),
                               "occupation": "Remex"},
                              {"start": str_datetime("2017-08-07 18:24:33.324733"),
                               "end": str_datetime("2017-08-07 18:34:33.324733"),
                               "occupation": "Inno"},
                              {"start": str_datetime("2017-08-09 17:14:33.324733"),
                               "end": str_datetime("2017-08-09 18:24:33.324733"),
                               "occupation": "OnPrEx"}])
    online_df.to_csv(online_df_path, index=False, sep="\t")

    result = pd.DataFrame([{"start": str_datetime("2017-08-06 18:24:33.324733"),
                            "end": str_datetime("2017-08-06 18:44:33.324733"),
                            "occupation": "RemEx"},
                           {"start": str_datetime("2017-08-07 18:24:33.324733"),
                            "end": str_datetime("2017-08-07 18:34:33.324733"),
                            "occupation": "Inno"},
                           {"start": str_datetime("2017-08-08 17:14:33.324733"),
                            "end": str_datetime("2017-08-08 18:24:33.324733"),
                            "occupation": "Inno"},
                           {"start": str_datetime("2017-08-09 17:14:33.324733"),
                            "end": str_datetime("2017-08-09 18:24:33.324733"),
                            "occupation": "OnPrEx"}])
    result = result.sort_values("start").reset_index(drop=True)
    yield {"result": result,
           "offline_df": offline_df,
           "offline_df_path": offline_df_path,
           "online_df": online_df,
           "online_df_path": online_df_path}
    # file_cleanup
    if os.path.isfile(offline_df_path):
        os.remove(offline_df_path)
    if os.path.isfile(online_df_path):
        os.remove(online_df_path)

@pytest.fixture()
def DbBaseClass_worker(test_data, monkeypatch):
    monkeypatch.setattr('work_tracker.functions.base_classes.DbBaseClass.get_pandas_now',
                        mock_time_short_break)
    monkeypatch.setattr('work_tracker.functions.base_classes.DbBaseClass.get_remote_db',
                        mock_True)
    monkeypatch.setattr('work_tracker.functions.base_classes.DbBaseClass.push_remote_db',
                        mock_True)
    monkeypatch.setattr('pysftp.CnOpts', mock_pysftp_CnOpts)
    db_worker = DbBaseClass("../tests/test_data/test_user_config_update_work_db.ini")
    db_worker.load_config()
    db_worker.db = db_worker.load_db(db_worker.db_path_offline)
    # mocking the today value
    db_worker.today = datetime.datetime(2017, 8, 8, 0, 0, 0, 0)
    db_worker.tomorrow = datetime.datetime(2017, 8, 9, 0, 0, 0, 0)
    return db_worker

def test_load_db_missing_file(DbBaseClass_worker):
    DbBaseClass_worker.db = DbBaseClass_worker.load_db("")
    new_df = pd.DataFrame([{"start": mock_time_short_break(),
                            "end": mock_time_short_break(),
                            "occupation": "TestOccupation1"}])
    assert_frame_equal(DbBaseClass_worker.db, new_df)

def test_clean_db(DbBaseClass_worker):
    orig_db = DbBaseClass_worker.db.copy()
    new_row = pd.DataFrame([{"start": str_datetime("2017-08-08 18:39:33.0"),
                             "end": str_datetime("2017-08-08 18:39:33.0"),
                             "occupation": "Inno"}])
    DbBaseClass_worker.db = DbBaseClass_worker.db.append(new_row, ignore_index=True).copy()
    DbBaseClass_worker.clean_db()
    assert_frame_equal(DbBaseClass_worker.db, orig_db, check_exact=True)



def test_load_db(DbBaseClass_worker, test_data):
    DbBaseClass_worker.db = DbBaseClass_worker.load_db(DbBaseClass_worker.db_path_offline)
    assert_frame_equal(DbBaseClass_worker.db, test_data["offline_df"])

def test_merge_dbs(DbBaseClass_worker, test_data):
    new_df = DbBaseClass_worker.merge_dbs()
    new_df = new_df.reset_index(drop=True)
    assert_frame_equal(new_df, test_data["result"], check_exact=True)

def test_merge_dbs_both_same(DbBaseClass_worker, test_data):
    DbBaseClass_worker.db_path_online = DbBaseClass_worker.db_path_offline
    new_df = DbBaseClass_worker.merge_dbs()
    new_df = new_df.reset_index(drop=True)
    assert_frame_equal(new_df, test_data["offline_df"], check_exact=True)
