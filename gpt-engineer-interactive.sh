PROMPT=$PWD/basic-app/prompt
while true;
do
    if [ -f $PROMPT && -z $1 ]; then
        SAVE_PROMPT=${PROMPT}_$(date '+%Y%m%d%H%M%S')
        mv $PROMPT $SAVE_PROMPT
    fi
    bash ./gpt-engineer.sh
done
