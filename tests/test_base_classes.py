# -*- coding: utf-8 -*-
"""
@file: test_update_work_db.py
@author: Sebastian Weigand
"""

import datetime
import pytest
import pandas as pd
from pandas.util.testing import assert_frame_equal

from work_tracker.functions.helpfer_functions import str_datetime
from work_tracker.functions.base_classes import DbBaseClass
from tests.custom_mocks import (
    mock_time_short_break,
    mock_True,
    mock_pysftp_CnOpts,
    mockDatetimeNow,
)

# from work_tracker.functions.helpfer_functions import debug_printer


@pytest.fixture(scope="function")
def DbBaseClass_worker(test_data_base, monkeypatch):
    db_worker = DbBaseClass("../tests/test_data/test_user_config_update_work_db.ini")
    return db_worker


def test_get_pandas_now(DbBaseClass_worker, monkeypatch):
    monkeypatch.setattr("datetime.datetime", mockDatetimeNow)
    assert DbBaseClass_worker.get_pandas_now() == pd.to_datetime(
        "2017-08-08 18:29:33.000000"
    )


def test_CnOpts_exception(DbBaseClass_worker, monkeypatch, capsys):
    monkeypatch.setattr("pysftp.CnOpts", lambda: {})
    DbBaseClass_worker.load_config()
    captured = capsys.readouterr()
    assert captured.out == "pysftp.CnOpts() doesn't exist\n"


def test_get_remote_db(DbBaseClass_worker, sftpserver, capsys):
    assert not DbBaseClass_worker.get_remote_db()
    # just prevents printing of Failed to get remote_db
    capsys.readouterr()
    with sftpserver.serve_content(
        {"test_folder": {"test_file.csv": "test file content"}}
    ):
        DbBaseClass_worker.load_config()
        new_login = {
            "host": sftpserver.host,
            "username": "user",
            "password": "pw",
            "port": sftpserver.port,
        }
        orig_login = DbBaseClass_worker.login_dict
        DbBaseClass_worker.login_dict = {**orig_login, **new_login}
        assert DbBaseClass_worker.get_remote_db()
        with open(DbBaseClass_worker.db_path_online) as retrived_file:
            assert retrived_file.read() == "test file content"


@pytest.fixture()
def mocked_DbBaseClass_worker(test_data_base, monkeypatch):
    monkeypatch.setattr(
        "work_tracker.functions.base_classes.DbBaseClass.get_pandas_now",
        mock_time_short_break,
    )
    monkeypatch.setattr(
        "work_tracker.functions.base_classes.DbBaseClass.get_remote_db", mock_True
    )
    monkeypatch.setattr(
        "work_tracker.functions.base_classes.DbBaseClass.push_remote_db", mock_True
    )
    monkeypatch.setattr("pysftp.CnOpts", mock_pysftp_CnOpts)
    db_worker = DbBaseClass("../tests/test_data/test_user_config_update_work_db.ini")
    db_worker.load_config()
    db_worker.db = db_worker.load_db(db_worker.db_path_offline)
    # mocking the today value
    db_worker.today = datetime.datetime(2017, 8, 8, 0, 0, 0, 0)
    db_worker.tomorrow = datetime.datetime(2017, 8, 9, 0, 0, 0, 0)
    return db_worker


def test_load_db_missing_file(mocked_DbBaseClass_worker):
    mocked_DbBaseClass_worker.db = mocked_DbBaseClass_worker.load_db("")
    new_df = pd.DataFrame(
        [
            {
                "start": mock_time_short_break(),
                "end": mock_time_short_break(),
                "occupation": "TestOccupation1",
            }
        ]
    )
    assert_frame_equal(mocked_DbBaseClass_worker.db, new_df)


def test_clean_db(mocked_DbBaseClass_worker):
    orig_db = mocked_DbBaseClass_worker.db.copy()
    new_row = pd.DataFrame(
        [
            {
                "start": str_datetime("2017-08-08 18:39:33.0"),
                "end": str_datetime("2017-08-08 18:39:33.0"),
                "occupation": "Inno",
            }
        ]
    )
    mocked_DbBaseClass_worker.db = mocked_DbBaseClass_worker.db.append(
        new_row, ignore_index=True
    ).copy()
    mocked_DbBaseClass_worker.clean_db()
    assert_frame_equal(mocked_DbBaseClass_worker.db, orig_db, check_exact=True)


def test_load_db(mocked_DbBaseClass_worker, test_data_base):
    mocked_DbBaseClass_worker.db = mocked_DbBaseClass_worker.load_db(
        mocked_DbBaseClass_worker.db_path_offline
    )
    assert_frame_equal(mocked_DbBaseClass_worker.db, test_data_base["offline_df"])


def test_merge_dbs(mocked_DbBaseClass_worker, test_data_base):
    new_df = mocked_DbBaseClass_worker.merge_dbs()
    new_df = new_df.reset_index(drop=True)
    assert_frame_equal(new_df, test_data_base["result"], check_exact=True)


def test_merge_dbs_both_same(mocked_DbBaseClass_worker, test_data_base):
    mocked_DbBaseClass_worker.db_path_online = mocked_DbBaseClass_worker.db_path_offline
    new_df = mocked_DbBaseClass_worker.merge_dbs()
    new_df = new_df.reset_index(drop=True)
    assert_frame_equal(new_df, test_data_base["offline_df"], check_exact=True)
