#!/usr/bin/env bash

# approach taken from:
# https://codefather.tech/blog/bash-get-script-directory/
script_dir=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
current_dir=$PWD
# go back to the current directory even if the script is interrupted
trap "cd $PWD" EXIT

cd "$script_dir/src"
python3 -m icaltool.icaltool "$@"
cd $PWD
