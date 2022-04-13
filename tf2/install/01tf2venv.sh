#!/usr/bin/env bash

# if no python virtual environment exists, then create it
if [ ! -f env/bin/activate ]; then
	python3.10 -m venv env
fi

# activate the environment
source env/bin/activate

# upgrade pip
pip install --upgrade pip

# deactivate the environment
deactivate

