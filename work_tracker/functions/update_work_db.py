# -*- coding: utf-8 -*-
"""
@file: update_work_db.py
@author: Sebastian Weigand
"""
# import configparser
import datetime

# import os

# import numpy as np
import pandas as pd

# import pysftp

from .helpfer_functions import get_abs_path, seconds_to_hm, get_midnight_datetime
from .base_classes import DbBaseClass


class DbInteraction(DbBaseClass):
    default_config_path = get_abs_path("default_config.ini")

    def __init__(self, user_config_path=".user_config.ini"):
        super().__init__(user_config_path)
        self.occupation = "TestOccupation"
        self.load_config()
        self.update_now_and_tomorrow()
        self.db = self.load_db(self.db_path_offline)
        self.clean_db()

    def change_occupation(self, occupation):
        # update the end of last occupation work
        self.update_db_locale()
        self.clean_db()
        self.occupation = occupation
        new_day_df = pd.DataFrame(
            [
                {
                    "start": self.get_pandas_now(),
                    "end": self.get_pandas_now(),
                    "occupation": self.occupation,
                }
            ]
        )
        self.db = self.db.append(new_day_df, ignore_index=True, sort=False)
        # just for writing changes to db
        self.update_db_locale()

    def get_today(self):
        """

        Returns
        -------
        today at midnight : datetime.datetime
            datetime.datetime.now() but with the hours, minutes, seconds, microseconds set to 0
        """
        return get_midnight_datetime(self.get_datetime_now())

    def update_now_and_tomorrow(self):
        """
        Updates the instance variables yesterday, today and tomorrow,
        in case the date has changed during the session.
        Preventing error in self.update_db_locale, due to a wrong date.
        """
        self.yesterday = self.get_today() - datetime.timedelta(1)
        self.today = self.get_today()
        self.tomorrow = self.get_today() + datetime.timedelta(1)

    def load_config(self):
        """
        Loads the config files to obtain the login for the SFTP server and the last occupation
        """
        config = super().load_config()

        occupations = config.get("occupation", "occupations").split(",")
        last_occupation = config.get("occupation", "last_occupation")
        if last_occupation in occupations:
            self.occupation = last_occupation

    def get_session_time(self):
        """
        Calculates the time a session (today) lasted and returns the string representation
        in hours and minutes

        Returns
        -------
        session_time : str
            string representation in hours and minutes
        """
        today_db = self.db.loc[self.db["start"] >= self.today]
        session_work = today_db["end"] - today_db["start"]
        return seconds_to_hm(session_work.sum().seconds)

    def get_start_time(self):
        """

        Returns
        -------
        %h:%M representation of the start time : str
            String representing start time as %h:%M
        """
        today_db = self.db.loc[self.db["start"] >= self.today]
        start_time = today_db["start"].min() - self.today
        return seconds_to_hm(start_time.seconds)

    def update_db_locale(self):
        self.update_now_and_tomorrow()
        # case all session today
        today_df = self.db[
            (self.db["start"] >= self.today) & (self.db["start"] < self.tomorrow)
        ]
        start_was_today = len(today_df.index)
        # case date changed during session
        yesterday_df = self.db[
            (self.db["start"] >= self.yesterday) & (self.db["start"] < self.today)
        ]
        start_was_yesterday = len(yesterday_df.index)
        # short pause is less than 10min which prevents resets by crashes
        if start_was_today:
            is_short_break = self.get_pandas_now() - today_df[
                "end"
            ].max() < pd.to_timedelta(
                "10m"
            )  # 10 minutes
        elif start_was_yesterday:
            is_short_break = self.get_pandas_now() - yesterday_df[
                "end"
            ].max() < pd.to_timedelta(
                "10m"
            )  # 10 minutes
        else:
            is_short_break = False
        if start_was_today and is_short_break:
            irow = self.db["end"].isin([today_df["end"].values.max()])
            self.db.loc[irow, "end"] = self.get_pandas_now()
        elif start_was_yesterday and is_short_break:
            irow = self.db["end"].isin([yesterday_df["end"].values.max()])
            self.db.loc[irow, "end"] = self.today
            new_day_df = pd.DataFrame(
                [
                    {
                        "start": self.today,
                        "end": self.get_pandas_now(),
                        "occupation": self.occupation,
                    }
                ]
            )
            self.db = self.db.append(new_day_df, ignore_index=True, sort=False)

        else:
            new_day_df = pd.DataFrame(
                [
                    {
                        "start": self.get_pandas_now(),
                        "end": self.get_pandas_now(),
                        "occupation": self.occupation,
                    }
                ]
            )
            self.db = self.db.append(new_day_df, ignore_index=True, sort=False)
        self.db.sort_values("start").reset_index(drop=True, inplace=True)
        self.db.to_csv(
            self.db_path_offline,
            index=False,
            columns=["start", "end", "occupation"],
            sep="\t",
        )
        return self.get_start_time(), self.get_session_time()

    def start_session(self):
        self.get_remote_db()
        # print("b4 merge\n", self.db)
        self.db = self.merge_dbs()
        # print("b4 update\n", self.db)
        self.update_db_locale()
        self.local_files = self.calc_file_hashes()
        # print("after update\n", self.db)
        self.push_remote_db()
