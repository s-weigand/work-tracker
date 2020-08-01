# -*- coding: utf-8 -*-
"""Module containing the baseclass for data interactions."""
import datetime
import os
from configparser import ConfigParser

import pandas as pd
import pysftp

from .helpfer_functions import get_abs_path, hash_file


class DbBaseClass:
    default_config_path = get_abs_path("default_config.ini")

    def __init__(self, user_config_path=".user_config.ini"):
        """
        Baseclass for data interactions.

        Parameters
        ----------
        user_config_path : str, optional
            Path to the user specific config, which will overwrite default settings.
            by default ".user_config.ini"

        """
        self.user_config_path = get_abs_path(user_config_path)

    def get_pandas_now(self) -> pd.Timestamp:  # type: ignore
        """
        Return datetime.now as pd.Timestamp.

        Returns
        -------
        pd.Timestamp:
            current time as timestamp: pd.Timestamp
        """
        return pd.to_datetime(datetime.datetime.now())

    def get_datetime_now(self) -> datetime.datetime:  # noqa: D401
        """
        Convenience method for mocking of datetime.datetime.now() in unittests.

        Returns
        -------
        datetime.datetime:
            datetime.now()

        """
        return datetime.datetime.now()

    def load_config(self) -> ConfigParser:
        """Load the config files and sets all necessary properties."""
        config = ConfigParser()
        config.read([self.default_config_path, self.user_config_path])

        self.data_folder_path = get_abs_path(
            config.get("paths", "data_folder", fallback="../data")
        )

        self.db_path_offline: str = os.path.join(self.data_folder_path, "local_db.tsv")
        self.db_path_online: str = os.path.join(self.data_folder_path, "remote_db.tsv")
        self.manual_db_path: str = os.path.join(self.data_folder_path, "manual_db.tsv")
        self.contract_info_path: str = os.path.join(self.data_folder_path, "contract_info.tsv")

        self.local_files = pd.DataFrame(
            {
                "local_db": {"path": self.db_path_offline},
                "manual_db": {"path": self.manual_db_path},
                "contract_info": {"path": self.contract_info_path},
            }
        ).T

        host = config.get("login", "host")
        username = config.get("login", "username")
        password = config.get("login", "password")
        port = config.get("login", "port", fallback=22)
        self.db_path = config.get("login", "db_path")
        self.login_dict = {
            "host": host,
            "username": username,
            "password": password,
            "port": port,
        }

        occupations = config.get("occupation", "occupations").split(",")
        last_occupation = config.get("occupation", "last_occupation")
        if last_occupation in occupations:
            self.occupation = last_occupation

        # preventing some errors with different versions of pysftp
        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None  # disable host key checking.

            self.login_dict["cnopts"] = cnopts
        except Exception:
            print("pysftp.CnOpts() doesn't exist")

        # returning config so subclasses and use it to obtain more information if needed
        return config

    def load_db(self, db_path: str) -> pd.DataFrame:
        """
        Read in the db file if it exists or creates a new one.

        Parameters
        ----------
        db_path : str
            path to the db_file on the SFTP server

        Returns
        -------
        pd.Dataframe
            Loaded database.

        """
        if not os.path.isfile(db_path):
            return pd.DataFrame(
                [
                    {
                        "start": self.get_pandas_now(),
                        "end": self.get_pandas_now(),
                        "occupation": self.occupation,
                    }
                ]
            )
        else:
            return pd.read_csv(db_path, parse_dates=["start", "end"], sep="\t")  # type: ignore

    def clean_db(self) -> None:
        """Remove rows where the session work was less than 1min."""
        work_time = self.db["end"] - self.db["start"]  # pylint: disable=E0203
        real_work_period = work_time > pd.to_timedelta(1, unit="m")  # 1 minute
        self.db = self.db[real_work_period]

    def calc_file_hashes(self) -> pd.DataFrame:
        """
        Calculate hashvalues for files.

        Returns
        -------
        pd.DataFrame
            Dataframe with file hashes.
        """
        local_files = self.local_files.copy()
        local_files["hashes"] = local_files["path"].apply(hash_file)
        return local_files

    def get_remote_db(self) -> bool:
        """
        Download the db_file to db_path_online from the SFTP server.

        This uses the values specified at ["login"]["db_path"] in the config file.

        Returns
        -------
        bool
            Wether database retrieval succeeded oder not.
        """
        try:
            with pysftp.Connection(**self.login_dict) as sftp:
                sftp.get(self.db_path, localpath=self.db_path_online, preserve_mtime=True)
            return True
        except Exception:
            print("Failed to get remote_db")
            return False

    def push_remote_db(self) -> bool:
        """
        Push the db_file from db_path_offline to the SFTP server.

        This uses the values specified at ["login"]["db_path"] in the config file.

        Returns
        -------
        bool
            Wether database upload succeeded oder not.
        """
        try:
            with pysftp.Connection(**self.login_dict) as sftp:
                sftp.put(self.db_path_offline, remotepath=self.db_path, preserve_mtime=True)
            return True
        except Exception:
            print("Failed to push remote_db")
            return False

    def merge_dbs(self) -> pd.DataFrame:
        """
        Merge local db with remote db.

        The overlap (same start) is replaced with the max value of end.

        Returns
        -------
        pd.Dataframe
            Local db merged with remote db, with striped overlap.
        """
        remote_db = self.load_db(self.db_path_online)
        if not self.db.equals(remote_db):
            new_db = pd.merge(
                self.db,
                remote_db,
                on=["occupation", "start", "end"],  # type: ignore
                how="outer",
            )
            # get conflicting start values (same start value different end value)
            start_fix = new_db["start"][new_db["start"].duplicated()]
            drop_list = []
            for start_val in start_fix.values:
                dup_index = new_db.index[new_db["start"].isin([start_val])]
                max_end_ts = new_db["end"].loc[dup_index].max()
                new_db.at[dup_index[0], "end"] = max_end_ts
                drop_list.append(dup_index[1:])
            flat_drop_list = [item for sublist in drop_list for item in sublist]
            new_db.drop(new_db.index[flat_drop_list], inplace=True)
        else:
            new_db = self.db
        new_db.drop_duplicates()
        return new_db.sort_values(["start"]).reset_index(drop=True)
