#!/bin/bash

open_browser() {
    local path="$1"
    OS_NAME=$(uname)

    if [[ "$OS_NAME" == "Linux" ]]; then
        if grep -qi microsoft /proc/version; then
            # WSL
            ABS_FILE_PATH=$(realpath "$path")
            WIN_PATH=$(wslpath -w "$ABS_FILE_PATH")
            cmd.exe /C start "" "$WIN_PATH" > /dev/null 2>&1
        else
            xdg-open "$path"
        fi
    elif [[ "$OS_NAME" == "Darwin" ]]; then
        open "$path"
    elif [[ "$OS_NAME" == MINGW* || "$OS_NAME" == CYGWIN* || "$OS_NAME" == MSYS* ]]; then
        cmd.exe /C start "" "$path" > /dev/null 2>&1
    else
        echo "Cannot detect OS for opening browser"
    fi
}

PULL_FROM_PATH="../data"
SAVE_TO_PATH="../plots" 

if [ "$1" == "clean" ]; then
    shopt -s nullglob
    rm "$SAVE_TO_PATH"/*.html
    echo "Cleared plots folder."
    exit 0
fi

if [ $# -lt 2 ]; then
    echo ""
    echo ""
    echo "This program automates usage for visualize.py, found in the same folder."
    echo " -- Usage is expected after the user generates a tree with treeGen.py to the data folder."
    echo " -- Paths are defined per the structure of the project, only names of trees and files are needed."
    echo " -- See usage statement for visualize.py for more information."
    echo ""
    echo "To generate a figure and open it within the browser:"
    echo "Usage: $0 <root_name> <plot_file_name>"
    echo ""
    echo "To view an already generated figure in the browser:"
    echo "Usage: $0 view <file_path>"
    echo ""
    echo "To clear the plots folder of all figures:"
    echo "Usage: $0 clean"
    echo ""
    echo ""
    exit 1
fi

if [ "$1" == "view" ]; then
    FILE_NAME="$SAVE_TO_PATH/$2.html"
    echo "Viewing: $2.html"
    open_browser "$FILE_NAME"
else
    ROOT="$PULL_FROM_PATH/$1"
    FILE_NAME="$SAVE_TO_PATH/$2.html"
    python3 visualize.py "$ROOT" "$FILE_NAME"
    open_browser "$FILE_NAME"
    echo "Viewing: $2.html"
fi


