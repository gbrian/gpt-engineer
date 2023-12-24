VOLUME_PATH=$(cd $1 && echo $PWD)
shift
docker run --rm -it -e OPENAI_API_KEY=$OPENAI_API_KEY -v $VOLUME_PATH:$VOLUME_PATH gpt-engineer $VOLUME_PATH $@
