VOLUME_PATH=$PWD
echo "Running gpt-engineer docker at VOLUME: $VOLUME_PATH"
docker run --rm -it -e OPENAI_API_KEY=$OPENAI_API_KEY -v $VOLUME_PATH:$VOLUME_PATH gpt-engineer $@
