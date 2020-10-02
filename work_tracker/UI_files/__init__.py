"""Package containing the UI files."""

import os
import sys

MODULE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, MODULE_PATH)
# this is needed for Ui_work_tracker to find icons_rc
MODULE_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, MODULE_PATH)
