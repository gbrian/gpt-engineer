#!/bin/bash
FULL_PATH_TO_SCRIPT="$(realpath "${BASH_SOURCE[-1]}")"
SCRIPT_DIRECTORY="$(dirname "$FULL_PATH_TO_SCRIPT")"
VENV_PATH=$SCRIPT_DIRECTORY/.venv
cd $SCRIPT_DIRECTORY

if [ "$1" == "docker" ]; then
  docker build -t gpt-engineer -f docker/Dockerfile .
else
  codx python_311
  python3 -m venv $VENV_PATH
  source $VENV_PATH/bin/activate
  pip install -e .
fi