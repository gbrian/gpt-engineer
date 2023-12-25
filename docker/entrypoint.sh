#!/bin/bash
project_dir=$1
shift

# Run the gpt engineer script
cd $project_dir
gpt-engineer $project_dir "$@"

# Patch the permissions of the generated files to be owned by nobody except prompt file
for item in "$project_dir"/*; do
    if [[ "$item" != "$project_dir/prompt" ]]; then
        chown -R nobody:nogroup "$item"
        chmod -R 777 "$item"
    fi
done
