#!/bin/bash
VENV_PATH=$PWD/.venv
WEB_PORT=${1:-8001}
API_PORT=${1:-8000}
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
kill -9 $(ps aux | grep -e "--port $WEB_PORT" | awk '{print $2}')
kill -9 $(ps aux | grep -e "--port $API_PORT" | awk '{print $2}')

bash -c "cd gpt_engineer/api/client_chat && npm run dev -- --port $WEB_PORT" &
gpt-engineer --api --port $API_PORT
