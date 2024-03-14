#!/bin/bash
FULL_PATH_TO_SCRIPT="$(realpath "${BASH_SOURCE[-1]}")"
SCRIPT_DIRECTORY="$(dirname "$FULL_PATH_TO_SCRIPT")"
VENV_PATH=$SCRIPT_DIRECTORY/.venv
cd $SCRIPT_DIRECTORY

codx python_311
python3.11-venv -m venv $VENV_PATH
source $VENV_PATH/bin/activate
pip install -e .
