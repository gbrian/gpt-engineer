#!/bin/bash
VENV_PATH=$PWD/.venv
export WEB_PORT=${WEB_PORT:-8001}
export API_PORT=${API_PORT:-8000}
export API_URL="http://localhost:$API_PORT"
if [ ! -d "$VENV_PATH" ]; then
  echo "Installing gpt-engineer at $VENV_PATH"
  python3 -m venv $VENV_PATH
  pip install -e .
  cd gpt_engineer/api/client_chat && bash -c "npm i"
fi
function clean () {
  echo "Cleaning..."
  
  ps aux | grep -e "gpt-engineer/"
  ps aux | grep -e "gpt-engineer/" | awk '{print $2}' | xargs kill -9 $1
}
trap clean SIGINT
clean

echo "Running gpt-engineer at $VENV_PATH - Home: $HOME"
# run api
source $VENV_PATH/bin/activate
. ~/.bashrc
gpt-engineer --api --port $API_PORT &
cd gpt_engineer/api/client_chat
npm i
npm run dev &
read
clean
