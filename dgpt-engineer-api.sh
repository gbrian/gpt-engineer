#!/bin/bash
PORT=$1
PROJECT_PATHS=$2

if [ ! "$PORT" ] || [ ! "$PROJECT_PATHS" ]; then
  echo "USAGE: dgpt-engineer.sh CLIENT_PORT PROJECT_PATHS"
else

  VOLUME_PATHS=""

  for path in $PROJECT_PATHS; do
    VOLUME_PATHS+="-v $path:$path "
  done

  GPT_USER="\"$(id -u):$(id -g)\""
  if [ "$(id -u)" == "0" ]; then
    GPT_USER="root"
  fi

  CMD="docker run --rm -it \
    -u $GPT_USER \
    -e DEBUG=${DEBUG:-1} \
    -p $PORT:8001 \
    ${VOLUME_PATHS}
    -v /root/codx-cli:/gpt \
    -v /var/run/docker.sock:/var/run/docker.sock \
    debian ls -l /gpt"

  echo "$CMD"

  $CMD
fi