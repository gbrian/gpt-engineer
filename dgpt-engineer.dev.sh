VOLUME_PATH=$PWD
echo "Running gpt-engineer docker at VOLUME: $VOLUME_PATH"
docker run --rm -it \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e DEBUG=1 \
  -v $VOLUME_PATH:$VOLUME_PATH \
  -v $PWD:/app \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gpt-engineer gpt-engineer $VOLUME_PATH $@
