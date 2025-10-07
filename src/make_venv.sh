#!/bin/bash
# Where the script itself is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Folder to make venv in
FOLDER_PATH="$(cd "$SCRIPT_DIR/../.." && pwd)"

#echo "$SCRIPT_DIR"
#echo "$FOLDER_PATH"

# If the actualy activate file exists
if [ -f "$FOLDER_PATH/venv/bin/activate" ]; then
  # Activate venv and install dependencies
  source "$FOLDER_PATH/venv/bin/activate"
  pip3 install zss
  pip3 install matplotlib
  pip3 install igraph
  pip3 install plotly
else
  # Make the venv, then continue
  python3 -m venv "$FOLDER_PATH/venv"
  source "$FOLDER_PATH/venv/bin/activate"
  pip3 install zss
  pip3 install matplotlib
  pip3 install igraph
  pip3 install plotly
fi