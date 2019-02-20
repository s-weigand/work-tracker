# import os
# import sys
import configparser

# import traceback
from ..functions.update_work_db import DbInteraction, get_abs_path

from PyQt5 import QtCore, QtWidgets
from .auto_generated.UI_work_tracker import Ui_work_tracker

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:

    def _fromUtf8(s):
        return s


class updateThread(QtCore.QThread):
    """
    Separate thread to not block the Ui while updating the database
    """

    update_signal = QtCore.pyqtSignal(tuple)
    push_signal = QtCore.pyqtSignal()
    change_occupation_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, *args):
        super(updateThread, self).__init__(parent)
        self.db_worker = DbInteraction()
        self.db_worker.start_session()
        self.push_signal.connect(self.push_db)
        self.change_occupation_signal.connect(self.change_occupation)
        self.do_updates = True
        self.index = 0

    def run(self):
        update_tuple = self.db_worker.update_db_locale()
        self.update_signal.emit(update_tuple)
        if self.do_updates:
            QtCore.QTimer.singleShot(60000, self.run)

    def push_db(self):
        self.db_worker.push_remote_db()
        print("pushed")

    def change_occupation(self, occupation):
        self.db_worker.change_occupation(occupation)

    def __del__(self):
        self.wait()


class WorkTracker(QtWidgets.QWidget, Ui_work_tracker):
    default_config_path = DbInteraction.default_config_path

    def __init__(self, user_config_path=".user_config.ini", parent=None, *args):
        super(WorkTracker, self).__init__(parent)
        self.setupUi(self)
        self.user_config_path = get_abs_path(user_config_path)
        self.update_thread = updateThread()
        self.populate_occupations()
        self.occupation_comboBox.currentIndexChanged.connect(self.change_occupation)
        self.start_btn.clicked.connect(self.start_timer)
        self.stop_btn.clicked.connect(self.stop_timer)
        self.push_counter = 0
        self.start_btn.setEnabled(False)
        self.start_btn.setChecked(True)
        self.stop_btn.setEnabled(True)
        self.stop_btn.setChecked(False)
        #  prevent lag
        QtCore.QTimer.singleShot(100, self.init_update_thread)

    def init_update_thread(self):
        self.update_thread.update_signal.connect(self.update)
        self.start_timer()

    def populate_occupations(self):
        """
        Reads the config file and configures and populates the occupation_comboBox
        If last_occupation in the config file is set and is occupations the values of
        occupation_comboBox will be set to last_occupation
        """
        try:
            config = configparser.ConfigParser()
            config.read(
                [self.default_config_path, self.user_config_path], encoding="utf-8"
            )
            occupations = config.get("occupation", "occupations").split(",")
            self.occupation_comboBox.clear()
            self.occupation_comboBox.addItems(occupations)
            last_occupation = config.get("occupation", "last_occupation")
            if last_occupation in occupations:
                last_occupation_index = self.occupation_comboBox.findText(
                    last_occupation
                )
                self.occupation_comboBox.setCurrentIndex(last_occupation_index)
                self.change_occupation()
        except Exception:
            print("occupations couldn't be read from config")

    def change_occupation(self, *args):
        occupation = self.occupation_comboBox.currentText()
        self.update_thread.change_occupation_signal.emit(occupation)

    def save_last_occupation(self):
        try:
            last_occupation = self.occupation_comboBox.currentText()
            config = configparser.ConfigParser()
            config.read(
                [self.default_config_path, self.user_config_path], encoding="utf-8"
            )
            config.set("occupation", "last_occupation", last_occupation)
            with open(self.user_config_path, "w", encoding="utf-8") as configfile:
                config.write(configfile)
        except Exception:
            print("last occupation couldn't be saved to config")

    def stop_timer(self, time_str):
        """
        Event triggered when stop is pressed
        """
        self.start_btn.setEnabled(True)
        self.start_btn.setChecked(False)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setChecked(True)
        self.update_thread.do_updates = False
        #  prevent lag
        QtCore.QTimer.singleShot(200, self.update_thread.push_signal.emit)

    def start_timer(self):
        """
        Event triggered when start is pressed
        """
        self.start_btn.setEnabled(False)
        self.start_btn.setChecked(True)
        self.stop_btn.setEnabled(True)
        self.stop_btn.setChecked(False)
        self.update_thread.do_updates = True
        self.update_thread.run()

    def update(self, update_tuple):
        start_time_str, session_time_str = update_tuple
        self.start_time.display(start_time_str)
        self.session_time.display(session_time_str)
        self.push_counter += 1
        if self.push_counter == 10:
            self.push_counter = 0
            self.update_thread.push_signal.emit()

    def quit_handler(self):
        self.save_last_occupation()
        self.update_thread.push_signal.emit()
