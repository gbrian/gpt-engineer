PROJECT_DIR=$PWD/${1:-basic-app}
echo "Running gpt-engineer on $PROJECT_DIR"
docker run -it --env-file=.env \
    -v $PROJECT_DIR:/project \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $PWD/gpt_engineer:/app/gpt_engineer \
    gpt-engineer -i -v
