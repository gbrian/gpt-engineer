VOLUME_PATH=$PWD
echo "Running gpt-engineer docker at VOLUME: $VOLUME_PATH"
docker run --rm -it \
  -u $USER \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e DEBUG=${DEBUG:-1} \
  -e GPT_ENGINEER_METADATA_PATH=$GPT_ENGINEER_METADATA_PATH \
  -v $VOLUME_PATH:$VOLUME_PATH \
  -v $PWD:/app \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --workdir=$VOLUME_PATH \
  gpt-engineer gpt-engineer $VOLUME_PATH $@
