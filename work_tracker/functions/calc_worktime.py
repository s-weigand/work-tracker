# -*- coding: utf-8 -*-
"""
@file: calc_worktime.py
@author: Sebastian Weigand
"""
import os
# import sys
import datetime
# import configparser

# import numpy as np
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
# import pysftp
import holidays  # NOQA

from .update_work_db import get_abs_path
from .base_classes import DbBaseClass
# from .helpfer_functions import debug_printer


class WorktimeCalculator(DbBaseClass):
    default_config_path = get_abs_path("default_config.ini")

    def __init__(self,  user_config_path=".user_config.ini"):
        super(self.__class__, self).__init__(user_config_path)
        self.special_holidays = {}
        self.load_config()
        self.db = self.load_db()
        self.split_date_overlap_session()
        self.contract_worktime_df = self.generate_contract_worktime_df()
        self.holidays = self.init_holidays()

    def load_db(self):
        """
        Trys to load the database directly from the server if possible, else
        it loads the local database or throws an exception that isn't possible either.

        Returns
        -------

        db: pandas.DataFrame
            Database with the actually worked time

        """
        if self.get_remote_db() and os.path.isfile(self.db_path_online):
            return pd.read_csv(self.db_path_online, parse_dates=["start", "end"], sep="\t")
        elif os.path.isfile(self.db_path_offline):
            return pd.read_csv(self.db_path_offline, parse_dates=["start", "end"], sep="\t")
        else:
            raise Exception("There was no proper database file provided")

    def load_config(self):
        """
        Loads the config files to obtain the login for the SFTP server, the last occupation,

        """
        config = super(self.__class__, self).load_config()

        self.manual_db_path = get_abs_path(config.get("paths", "manual_db"))
        self.contract_info_path = get_abs_path(config.get("paths", "contract_info"))
        self.country = config.get("location", "country", fallback="")
        self.province = config.get("location", "province", fallback="")
        if 'special_holidays' in config.sections():
            self.special_holidays = config._sections['special_holidays']

    def generate_contract_worktime_df(self):
        """
        Generates a template like DataFrame containing the mean daily work time for each day
        counting as workday based on the contract details. This Template will be used later on
        to generate the manual_df and holiday_df.

        Returns
        -------

        contract_worktime_df:  pandas.DataFrame
            Dataframe containing all workdays and their mean daily working time,
            since the 1st contract started until now
        """
        contract_worktime_df = pd.DataFrame()
        contract_info_df = pd.read_csv(self.contract_info_path, parse_dates=["start"], sep="\t")
        for index, row in contract_info_df.iterrows():
            if index < contract_info_df.shape[0]-1:
                end_date = contract_info_df["start"].iloc[index + 1] - pd.to_timedelta("1D")
            else:
                end_date = self.db["end"].max()
            business_days = CustomBusinessDay(weekmask=row["weekmask"])
            start_values = pd.Series(pd.date_range(row["start"], end_date,
                                                   normalize=True, freq=business_days))

            # calculate the daily worktime depending on the interval and weekmask
            daily_worktime = self.get_daily_worktime(row["frequenzy"],
                                                     row["worktime"],
                                                     row["weekmask"])
            worktime_df = pd.DataFrame({"start": start_values})
            worktime_df["worktime"] = pd.to_timedelta(daily_worktime, unit="h")
            contract_worktime_df = contract_worktime_df.append(worktime_df)

        return contract_worktime_df.sort_values("start").reset_index(drop=True)

    def get_daily_worktime(self, frequenzy, worktime, weekmask):
        """
        Calculates the mean daily work time based on the contract details.

        Parameters
        ----------
        frequenzy: str
            Timeperiod in which the the user is supposed to to work worktime*1h
            Supported values are: monthly, weekly
        worktime: int, float
            Time in hours that the user is supposed to work in frequenzy
        weekmask: str
            Listing of the abbreviated weekdays the user is supposed to work
            i.e.: "Mon Tue Wed Thu Fri Sat"

        Returns
        -------

        daily_worktime:  float
        """
        # calculate the daily worktime depending on the interval and weekmask
        work_days_per_week = len(weekmask.split(" "))
        if frequenzy == "weekly":
            daily_worktime = worktime/work_days_per_week
        else:
            daily_worktime = (worktime*12)/(365-52*(7-work_days_per_week))
        return daily_worktime

    def get_holiday_df(self):
        """
        Generates a Dataframe containing all holidays from the start of the
        first contract until now, as well as work time
        based on the contract parameters for those days.

        Returns
        -------
        holiday_df: pandas.DataFrame
            Dataframe containing all holidays from the start of the
            first contract until now, as well as work time based on
            the contract parameters for those days.

        """
        is_holiday = (self.contract_worktime_df["start"].apply(lambda x: x in self.holidays))
        holiday_df = self.contract_worktime_df[is_holiday].copy()
        holiday_df["end"] = holiday_df["start"]
        holiday_df["occupation"] = "holiday"
        holiday_df.sort_values("start", inplace=True)
        return holiday_df[["start",
                           "end",
                           "occupation",
                           "worktime"]].reset_index(drop=True)

    def init_holidays(self):
        """
        Returns the class instance from holiday, which matches the country and province
        given in the config and updates it with the special holidays, also given in the config

        Returns
        -------

        holidays : class instance from holidays

        """
        # fallback in case country wasn't provided
        if self.country in dir(holidays):
            # get holidays class depending on the country
            country_class = getattr(holidays, self.country)
            # get holidays class depending on the country and province
            if self.province in country_class.PROVINCES:
                custom_holidays = country_class(state=self.province)
            else:
                custom_holidays = country_class()
            # update holidays with special_holidays, given in the config
            special_holiday_update_dict = {}
            # for year in pd.unique(self.contact_worktime_df.index.year):
            for year in pd.unique(self.contract_worktime_df["start"].dt.year):
                for key, val in self.special_holidays.items():
                    day = int(key.split("-")[0])
                    month = int(key.split("-")[1])
                    date = datetime.datetime(year, month, day)
                    special_holiday_update_dict[date] = val
            # add new holidays to custom_holidays
            custom_holidays.update(special_holiday_update_dict)
            return custom_holidays
        else:
            return []

    def get_manual_df_with_workime(self):
        """
        Read the manual_db file, which contains information like sick time | vacation,
        specified by manual_db in the config.
        Then expands the given time periods to date_ranges on a daily base, drops the none
        workdays and adds the daily work time based on the contract parameters for that day.

        Returns
        -------

        manual_df: pandas.DataFrame
            Dataframe containing the to a daily base expanded entry's of manual_df.
        """
        manual_df = pd.DataFrame()
        manual_db = pd.read_csv(self.manual_db_path, parse_dates=["start", "end"], sep="\t")
        # expand start and end date to a range of dates
        for index, row in manual_db.iterrows():
            new_df = pd.DataFrame()
            new_df["start"] = pd.date_range(row["start"], row["end"], normalize=True)
            new_df["end"] = pd.date_range(row["start"], row["end"], normalize=True)
            new_df["occupation"] = row["occupation"]
            manual_df = manual_df.append(new_df)

        # drop days which are holidays
        work_day = (manual_df["start"].apply(lambda x: x not in self.holidays))
        manual_df = pd.merge(manual_df[work_day], self.contract_worktime_df, on="start")
        return manual_df.sort_values("start").reset_index(drop=True)

    def split_date_overlap_session(self):
        """
        Splits sessions which contain midnight to to sessions.
        The first lasting until midnight and the second starting at midnight.

        i.e.:
            df before:
            start   end
            1.1.1970 21:00:00   2.1.1970 02:00:00

            df after:
            start   end
            1.1.1970 21:00:00   2.1.1970 00:00:00
            2.1.1970 00:00:00   2.1.1970 02:00:00
        """
        # midnight of the start and end date, are at different dates
        overlap_sessions = self.db["start"].dt.normalize() != self.db["end"].dt.normalize()
        # copy overlapping part from the df
        df_to_append = self.db[overlap_sessions].copy()
        # set start date of the df to append to midnight
        df_to_append.loc[:, "start"] = df_to_append["end"].dt.normalize()
        # set the end date of the overlapping df to midnight
        self.db.loc[overlap_sessions, "end"] = self.db[overlap_sessions]["end"].dt.normalize()
        self.db = self.db.append(df_to_append)
        self.db = self.db[(self.db["end"] - self.db["start"]) > pd.to_timedelta(1, unit="m")]
        self.db = self.db.sort_values("start").reset_index(drop=True)

    def get_total_df(self):
        self.db["worktime"] = self.db["end"] - self.db["start"]
        result_df = pd.concat([self.db, self.get_holiday_df(),
                               self.get_manual_df_with_workime()], sort=False)
        result_df = self.add_time_columns(result_df)
        result_df = result_df.sort_values(["start",
                                           "end"]).reset_index(drop=True)
        return result_df[['start', 'end', 'worktime', 'year',
                          'month', "week", 'day', 'occupation']]

    def add_time_columns(self, df, date_time_column="start"):
        """
        Adds Year, Month, Week and Day columns to an existing Dataframe

        Parameters
        ----------
        df: pandas.DataFrame

        date_time_column:

        Returns
        -------

        """
        result_df = df.copy()
        result_df["year"] = result_df[date_time_column].dt.year
        result_df["month"] = result_df[date_time_column].dt.month
        result_df["week"] = result_df[date_time_column].dt.week
        result_df["day"] = result_df[date_time_column].dt.day
        return result_df

    def get_plot_df(self, rule="D", date_time_column="start"):
        """
        Dataframe with a DateTimeIndex, columns named by occupation and
        containing the worked time of that occupation for the given samplingrate

        Parameters
        ----------
        rule : str
            resampling rule see pandas.DataFrame.resample

        Returns
        -------
        plot_df : pandas.DataFrame
            Dataframe with a DateDimeIndex, columns named by occupation and
            containing the worktime of that occupation for the samplingrate
        """
        total_df = self.get_total_df().sort_values(date_time_column).reset_index(drop=True)
        plot_df = pd.DataFrame(total_df.resample(rule, on=date_time_column).worktime.sum())
        plot_df.columns = ["total"]
        for occupation in total_df["occupation"].unique():
            occupation_series = total_df[total_df["occupation"] == occupation]
            occupation_series = occupation_series.resample(rule,
                                                           on=date_time_column).worktime.sum()
            occupation_series = occupation_series.rename(occupation)
            plot_df = plot_df.join(occupation_series)
        return plot_df.fillna(pd.Timedelta(seconds=0))
