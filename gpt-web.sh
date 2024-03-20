#!/bin/bash
VENV_PATH=$PWD/.venv

if [ ! -d "$VENV_PATH" ]; then
  echo "Installing gpt-engineer at $VENV_PATH"
  codx nodejs
  codx python_311
  python3 -m venv $VENV_PATH
  source $VENV_PATH/bin/activate
  pip install -e .
  cd gpt_engineer/api/client_chat && bash -c "npm i"
fi

# run api
source $VENV_PATH/bin/activate
# Stop running...
kill -9 $(ps aux | grep -e "--port 8001" | awk '{print $2}')
kill -9 $(ps aux | grep -e "--port 8000" | awk '{print $2}')

bash -c "cd gpt_engineer/api/client_chat && npm run dev" &
gpt-engineer --api --port 8000
