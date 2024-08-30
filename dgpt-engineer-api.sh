#!/bin/bash
PROJECT_PATHS=()
LOGS=0
CMD="/gpt-engineer/gpt-web.sh"
BUILD=0
PORT=8003

while [ "$1" != "" ]; do
  if [ "$1" == "-p" ]; then
    shift
    PORT=$1
  fi
  if [ "$1" == "-v" ]; then
    shift
    PROJECT_PATHS+=($1)
  fi
  if [ "$1" == "-c" ]; then
    shift
    CMD=$1
  fi
  if [ "$1" == "--logs" ]; then
    LOGS=1
  fi
  if [ "$1" == "--build" ]; then
    BUILD=1
  fi
  shift
done

if [ ! "$PORT" ] || [ ! "$PROJECT_PATHS" ]; then
  echo "USAGE: dgpt-engineer.sh -p CLIENT_PORT -v PROJECT_PATH_1 -v PROJECT_PATH_2 ... [--logs -c]

  -p      gpt-engineer web client port
  -v      Projects absolute paths
  -c      Overwrite default command gpt-wbe.sh
  --logs  Show logs
  "
else

  VOLUME_PATHS="-v /var/run/docker.sock:/var/run/docker.sock "
  for path in $PROJECT_PATHS; do
    VOLUME_PATHS+="-v $path:$path "
  done
  if [ "$DEBUG" != "" ]; then
    echo "DEBUG VERSION: Mapping local /gpt-engineer"
    VOLUME_PATHS+="-v $PWD:/gpt-engineer"
  fi

  if [ "$GPT_USER" == "" ]; then
    GPT_USER="\"$(id -u):$(id -g)\""
    if [ "$(id -u)" == "0" ]; then
      GPT_USER="root"
    fi
  fi

  IMAGE_EXISTS="$(docker image ls | grep gpt-engineer)"
  if [ "$IMAGE_EXISTS" == "" ] || [ "$BUILD" == "1" ];then
    docker build --progress=plain \
          --no-cache \
          --build-arg="GPT_USER=$(id -u)" \
          --build-arg="GPT_USER_GROUP=$(id -g)" \
          -t gpt-engineer -f docker/Dockerfile .
  fi
  
  CMD="docker run -d -it \
    -e DEBUG=${DEBUG:-1} \
    -e PROJECT_PATHS=$PROJECT_PATHS \
    -p $PORT:8001 \
     \
    $VOLUME_PATHS \
    --name gpt-engineer gpt-engineer $CMD"

  echo "$CMD LOGS: $LOGS"
  echo "Remove running container"
  docker rm -f gpt-engineer
  $CMD
  [ "$LOGS" == "1" ] && docker logs -f gpt-engineer
fi