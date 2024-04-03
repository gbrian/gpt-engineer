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

  if [ "$GPT_USER" == "" ]; then
    GPT_USER="\"$(id -u):$(id -g)\""
    if [ "$(id -u)" == "0" ]; then
      GPT_USER="root"
    fi
  fi

  docker build --progress=plain -t gpt-engineer -f docker/Dockerfile .

  CMD="docker run -d -it \
    -u $GPT_USER \
    -e DEBUG=${DEBUG:-1} \
    -p $PORT:8001 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $PWD:/gpt-engineer \
    $VOLUME_PATHS \
    --name gpt-engineer gpt-engineer /gpt-engineer/gpt-web.sh"

  echo "$CMD"
  echo "Remove running container"
  docker rm -f gpt-engineer
  $CMD
  [ "$3" == "--logs" ] && docker logs -f gpt-engineer
fi