#!/usr/bin/env bash

# Check the current working directory
correct_dir=1
for item in *; do
    file=$(basename ${item})
    if [[ "${file}" == "analysis" ]]; then
        correct_dir=0
        break
    fi
done

if [ ${correct_dir} -ne 0 ]; then
    echo 'You must run the script from the parent directory of analysis'
    exit 1
fi

# Check the number of arguments
if [ "$#" -lt 1 ]; then
    echo 'You must provide at least the path to the script'
    exit 1
fi


script="$1"
rest="${@:2}"

module=$(echo ${script} | tr '/' '.' | sed "s/\.py$//")  # replace slashes with points and remove trailing .py

if [ -z "${rest}" ]; then
    python -m ${module}
else
    python -m ${module} ${rest}
fi
