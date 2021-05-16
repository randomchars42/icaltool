#!/usr/bin/env bash

# approach taken from:
# https://codefather.tech/blog/bash-get-script-directory/
script_dir=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
source "$script_dir/venv/bin/activate"
echo "type 'deactivate' to deactivate (read more in 'note.md')"
