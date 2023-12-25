VOLUME_PATH=$PWD
echo "Running gpt-engineer docker at VOLUME: $VOLUME_PATH"
docker run --rm -it \
  -u $USER \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e VOLUME_PATH=$VOLUME_PATH \
  -v $VOLUME_PATH:$VOLUME_PATH \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gpt-engineer $@
