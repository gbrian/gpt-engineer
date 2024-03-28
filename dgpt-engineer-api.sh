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

  docker build --progress=plain -t gpt-engineer -f docker/Dockerfile .

  CMD="docker run -d -it \
    -u $GPT_USER \
    -e DEBUG=${DEBUG:-1} \
    -p $PORT:8001 \
    -v $PWD:$PWD \
    -v /var/run/docker.sock:/var/run/docker.sock \
    $VOLUME_PATHS \
    -w "$PWD" \
    --name gpt-engineer gpt-engineer $PWD/gpt-web.sh"

  echo "$CMD"
  echo "Remove running container"
  docker rm -f gpt-engineer
  $CMD
  docker logs -f gpt-engineer
fi