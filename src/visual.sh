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
SAVE_TO_PATH="../report/images" 

if [ "$1" == "clean" ]; then
    shopt -s nullglob
    rm "$SAVE_TO_PATH"/*.png
    echo "Cleared plots folder."
    exit 0

elif [ "$1" == "view" ]; then
    FILE_NAME="$SAVE_TO_PATH/$2"
    echo "Viewing: $2"
    open_browser "$FILE_NAME"

elif [ "$1" == "visual" ]; then
    
    ROOT="$PULL_FROM_PATH/$2"
    FILE_NAME="$SAVE_TO_PATH/$3"
    python3 visualize.py "visual" "$ROOT" "$FILE_NAME"
    open_browser "$FILE_NAME"
    echo "Generated png: $3"

elif [ "$1" == "compare" ]; then
    ROOT_A="$PULL_FROM_PATH/$2"
    ROOT_B="$PULL_FROM_PATH/$3"
    FILE_NAME="$SAVE_TO_PATH/$4"
    python3 visualize.py "compare" "$ROOT_A" "$ROOT_B" "$FILE_NAME"
    open_browser "$FILE_NAME"
    echo "Generated png: $4"

else
    echo ""
    echo ""
    echo "This program automates usage for visualize.py, found in the same folder."
    echo " -- Usage is expected after the user generates a tree with treeGen.py to the data folder."
    echo " -- Paths are defined per the structure of the project, only names of trees and files are needed."
    echo " -- See usage statement for visualize.py for more information."
    echo ""
    echo "To generate a figure and open it within the browser:"
    echo "Usage: $0 visual <root_name> <save_path>"
    echo ""
    echo "To generate a figure comparing two plots, and open it within the browser:"
    echo "Usage: $0 compare <original_root_name> <compare_root_name> <save_path>"
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


