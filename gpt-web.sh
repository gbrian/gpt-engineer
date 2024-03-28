#!/bin/bash
VENV_PATH=$PWD/.venv
WEB_PORT=${WEB_PORT:-8001}
API_PORT=${API_PORT:-8000}
if [ ! -d "$VENV_PATH" ]; then
  echo "Installing gpt-engineer at $VENV_PATH"
  python3 -m venv $VENV_PATH
  pip install -e .
  cd gpt_engineer/api/client_chat && bash -c "npm i"
fi

echo "Running gpt-engineer at $VENV_PATH - Home: $HOME"
# run api
source $VENV_PATH/bin/activate
. ~/.bashrc

gpt-engineer --api --port $API_PORT &
cd gpt_engineer/api/client_chat
npm i
npm run dev -- --port $WEB_PORT
