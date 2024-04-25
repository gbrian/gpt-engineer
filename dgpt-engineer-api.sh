#!/bin/bash
PORT=$1
PROJECT_PATHS=()
LOGS=0
CMD="/gpt-engineer/gpt-web.sh"

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
    docker image rm gpt-engineer
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

  if [ "$(docker image ls | grep gpt-engineer)" == "" ];then
    docker build --progress=plain \
          --build-arg="GPT_USER=$(id -u)" \chatvi
          --build-arg="GPT_USER_GROUP=$(id -g)" \
          -t gpt-engineer -f docker/Dockerfile .
  fi

  CMD="docker run -d -it \
    -e DEBUG=${DEBUG:-1} \
    -p $PORT:8001 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $PWD:/gpt-engineer \
    $VOLUME_PATHS \
    --name gpt-engineer gpt-engineer $CMD"

  echo "$CMD LOGS: $LOGS"
  echo "Remove running container"
  docker rm -f gpt-engineer
  $CMD
  [ "$LOGS" == "1" ] && docker logs -f gpt-engineer
fi