#!/bin/bash
CURREN_DIR=$PWD
FULL_PATH_TO_SCRIPT="$(realpath "${BASH_SOURCE[-1]}")"
SCRIPT_DIRECTORY="$(dirname "$FULL_PATH_TO_SCRIPT")"
VENV_PATH=$SCRIPT_DIRECTORY/.venv
cd $SCRIPT_DIRECTORY

if [ ! -d $VENV_PATH ]; then
  codx python_311
  python3 -m venv $VENV_PATH
  source $VENV_PATH/bin/activate
  pip install -e .  
fi
source $VENV_PATH/bin/activate
echo "Ruinning local gpt-enginner in $CURREN_DIR"
echo "GPTENG_PATH: $GPTENG_PATH"
gpt-engineer $CURREN_DIR $@
cd $CURREN_DIR