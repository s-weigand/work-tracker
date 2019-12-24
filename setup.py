#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click>=6.0",
    "pandas>=0.23.4",
    "PyQt5>=5.6.0",
    "pysftp>=0.2.9",
    "holidays>=0.9.8",
    "dash>=0.37.0",
]

setup_requirements = []

test_requirements = []

setup(
    author="Sebastian Weigand",
    author_email="s.weigand.phy@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.6",
    description="Simple tool to keep track of your work time and/or productivity ",
    entry_points={"console_scripts": ["work_tracker=work_tracker.cli:main",],},
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="work_tracker",
    name="work_tracker",
    packages=find_packages(include=["work_tracker"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/s-weigand/work-tracker",
    version="0.1.0",
    zip_safe=False,
)
