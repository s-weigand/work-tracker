import os
import pandas as pd
import pytest
from shutil import copyfile

from work_tracker.functions.helpfer_functions import get_abs_path

# ###########################
# #     DATA FIXTURES       #
# ###########################
@pytest.fixture(scope="module")
def data_test_calc():

    test_data_path = get_abs_path("../tests/test_data/calc_worktime")
    test_df_path_src = os.path.join(test_data_path, "base_remote_df.tsv")
    test_df_path_dest = os.path.join(test_data_path, "remote_db.tsv")
    copyfile(test_df_path_src, test_df_path_dest)
    test_df = pd.read_csv(test_df_path_src, sep="\t", parse_dates=["start", "end"])
    result = pd.read_csv(
        os.path.join(test_data_path, "base_result.tsv"),
        sep="\t",
        parse_dates=["start", "end"],
    )
    manual_df_path = os.path.join(test_data_path, "result_manual_db.tsv")
    manual_df = pd.read_csv(manual_df_path, parse_dates=["start", "end"], sep="\t")
    yield {
        "result": result,
        "test_df": test_df,
        "test_df_path": test_df_path_dest,
        "manual_df": manual_df,
    }
    # file_cleanup
    if os.path.isfile(test_df_path_dest):
        os.remove(test_df_path_dest)


@pytest.fixture(scope="function")
def test_data_base():
    test_data_path = get_abs_path("../tests/test_data/update_data")
    offline_df_path_src = os.path.join(test_data_path, "baseclass_offline_df.tsv")
    online_df_path_src = os.path.join(test_data_path, "baseclass_online_df.tsv")
    offline_df_path_dest = os.path.join(test_data_path, "local_db.tsv")
    online_df_path_dest = os.path.join(test_data_path, "remote_db.tsv")
    copyfile(offline_df_path_src, offline_df_path_dest)
    copyfile(online_df_path_src, online_df_path_dest)
    offline_df = pd.read_csv(
        offline_df_path_src, sep="\t", parse_dates=["start", "end"]
    )
    online_df = pd.read_csv(online_df_path_src, sep="\t", parse_dates=["start", "end"])
    result = pd.read_csv(
        os.path.join(test_data_path, "baseclass_result.tsv"),
        sep="\t",
        parse_dates=["start", "end"],
    )
    yield {
        "result": result,
        "offline_df": offline_df,
        "offline_df_path": offline_df_path_dest,
        "online_df": online_df,
        "online_df_path": online_df_path_dest,
    }
    # file_cleanup
    if os.path.isfile(offline_df_path_dest):
        os.remove(offline_df_path_dest)
    if os.path.isfile(online_df_path_dest):
        os.remove(online_df_path_dest)
