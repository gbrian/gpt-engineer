VOLUME_PATH=$PWD
echo "Running gpt-engineer docker at VOLUME: $VOLUME_PATH"
docker run --rm -it \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e DEBUG=$DEBUG \
  -e GPT_ENGINEER_METADATA_PATH=$GPT_ENGINEER_METADATA_PATH \
  -v $VOLUME_PATH:$VOLUME_PATH \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --workdir=$VOLUME_PATH \
  gpt-engineer gpt-engineer $VOLUME_PATH $@
