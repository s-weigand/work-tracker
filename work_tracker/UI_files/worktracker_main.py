"""Module containing the main GUI class."""

import configparser
from typing import Tuple, Union

from PyQt5 import QtCore, QtWidgets

from ..functions.update_work_db import DbInteraction, get_abs_path
from .auto_generated.UI_work_tracker import Ui_work_tracker

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:

    def _fromUtf8(s):
        return s


class updateThread(QtCore.QThread):

    update_signal = QtCore.pyqtSignal(tuple)
    push_signal = QtCore.pyqtSignal()
    change_occupation_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, *args):
        """Separate thread to not block the Ui while updating the database."""
        super().__init__(parent)
        self.db_worker = DbInteraction()
        self.db_worker.start_session()
        self.push_signal.connect(self.push_db)
        self.change_occupation_signal.connect(self.change_occupation)
        self.do_updates = True
        self.index = 0

    def run(self):
        """Functionality run by the thread."""
        update_tuple = self.db_worker.update_db_locale()
        self.update_signal.emit(update_tuple)
        if self.do_updates:
            QtCore.QTimer.singleShot(60000, self.run)

    def push_db(self):
        """Push the db_file from db_path_offline to the SFTP server."""
        self.db_worker.push_remote_db()
        print("pushed")

    def change_occupation(self, occupation):
        """Change value of db_worker.occupation."""
        self.db_worker.change_occupation(occupation)

    def __del__(self):
        """Handle deletion."""
        self.wait()


class WorkTracker(QtWidgets.QWidget, Ui_work_tracker):
    default_config_path = DbInteraction.default_config_path

    def __init__(
        self,
        user_config_path: str = ".user_config.ini",
        parent: Union[QtWidgets.QWidget, QtWidgets.QApplication, None] = None,
        *args,
    ):
        """
        Main-GUI widget.

        Parameters
        ----------
        user_config_path : str, optional
            Path to the user specific config, which will overwrite default settings.
            by default ".user_config.ini"
        parent : [type], optional
            Parent widget, by default None
        """
        super().__init__(parent)
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
        """Connect updatesignal to thread."""
        self.update_thread.update_signal.connect(self.update)
        self.start_timer()

    def populate_occupations(self):
        """
        Read the config file and configure and populate the occupation_comboBox.

        If last_occupation in the config file is set and is occupations the values of
        occupation_comboBox will be set to last_occupation
        """
        try:
            config = configparser.ConfigParser()
            config.read([self.default_config_path, self.user_config_path], encoding="utf-8")
            occupations = config.get("occupation", "occupations").split(",")
            self.occupation_comboBox.clear()
            self.occupation_comboBox.addItems(occupations)
            last_occupation = config.get("occupation", "last_occupation")
            if last_occupation in occupations:
                last_occupation_index = self.occupation_comboBox.findText(last_occupation)
                self.occupation_comboBox.setCurrentIndex(last_occupation_index)
                self.change_occupation()
        except Exception:
            print("occupations couldn't be read from config")

    def change_occupation(self, *args):
        """Change value of occupation in the combobox and thread."""
        occupation = self.occupation_comboBox.currentText()
        self.update_thread.change_occupation_signal.emit(occupation)

    def save_last_occupation(self):
        """Save current occupation to config."""
        try:
            last_occupation = self.occupation_comboBox.currentText()
            config = configparser.ConfigParser()
            config.read([self.default_config_path, self.user_config_path], encoding="utf-8")
            config.set("occupation", "last_occupation", last_occupation)
            with open(self.user_config_path, "w", encoding="utf-8") as configfile:
                config.write(configfile)
        except Exception:
            print("last occupation couldn't be saved to config")

    def stop_timer(self, time_str: str):
        """Event triggered when stop is pressed."""
        self.start_btn.setEnabled(True)
        self.start_btn.setChecked(False)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setChecked(True)
        self.update_thread.do_updates = False
        #  prevent lag
        QtCore.QTimer.singleShot(200, self.update_thread.push_signal.emit)

    def start_timer(self):
        """Event triggered when start is pressed."""
        self.start_btn.setEnabled(False)
        self.start_btn.setChecked(True)
        self.stop_btn.setEnabled(True)
        self.stop_btn.setChecked(False)
        self.update_thread.do_updates = True
        self.update_thread.run()

    def update(self, update_tuple: Tuple[str, str]):
        """Update GUI and send update signal to thread."""
        start_time_str, session_time_str = update_tuple
        self.start_time.display(start_time_str)
        self.session_time.display(session_time_str)
        self.push_counter += 1
        if self.push_counter == 10:
            self.push_counter = 0
            self.update_thread.push_signal.emit()

    def quit_handler(self):
        """Save occupation and push db before quitting."""
        self.save_last_occupation()
        self.update_thread.push_signal.emit()
