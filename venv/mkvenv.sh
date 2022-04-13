#!/usr/bin/env bash

# if no python virtual environment exists, then create it
if [ ! -f env/bin/activate ]; then
	python3.10 -m venv env
fi

# to activate the environment, simply type the command:
source env/bin/activate

# to deactivate the environment, simply type the command:
deactivate

