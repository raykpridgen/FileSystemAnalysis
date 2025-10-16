#!/bin/bash

# =================================================================
# This script automates the full file tree comparison workflow.
# =================================================================


param=$1

if [ -z "$param" ]; then
    echo ""
    echo ""
    echo "This program automates usage for all major executions in this project, found in the src folder."
    echo " -- Usage is expected for generating, modifying, plotting, and generating a report for a filesystem tree."
    echo ""
    echo "To execute this program, run:"
    echo "    $0 <iterations>"
    echo "Or, to clean data:"
    echo "    $0 clean"
    echo ""
    echo "Applicable python files that execute an operation in this script include:"
    echo ""
    echo "-- treeGen.py"
    echo "    Generates an artificial filesystem tree from many parameters that determine behavior."
    echo ""
    echo "-- modify.py"
    echo "    Modifies an artificial filesystem tree with random operations over given iterations."
    echo ""
    echo "-- visualize.py"
    echo "    Plots a visual graph representation of the tree generated, highlighting changes over iterations."
    echo ""
    echo "-- compare_trees.py"
    echo "    Computes useful metrics for the nature of the filesystem tree and it's changes over iterations."
    echo ""
    echo "-- report_generator.py"
    echo "    Generates a PDF report of all data generated, computed, and analyzed in this script."
    echo ""
    echo ""
    echo "For more specific information on a particular script, see the usage statement by running: "
    echo "    python3 <script>"
    echo ""
    exit 0

elif [ "$param" == "clean" ]; then
    shopt -s nullglob
    rm ../report/images/*.png
    > ../report/data/metrics.txt
    rm ../report/final_report.pdf
    echo "Cleared data"
    exit 0
fi
# --- 1. Define filenames and parameters ---

ORIGINAL_TREE_NAME="original_tree"
MODIFIED_TREE_BASE_NAME="modified_tree"

# Generate random parameters for trees.py
# Depth and Degree
TREES_MIN_DEPTH=$(( 5 ))
TREES_MAX_DEPTH=$(( 10 ))

# Generate random parameters for modify.py
# Max new files (0 - 3)
MAX_NEW_FILES=$(( 20 ))

# Hardcode iterations for testing purposes
ITERATIONS=$1

# Define GUFI index names
GUFI_ORIGINAL_INDEX="gufi_index_${ORIGINAL_TREE_NAME}"
GUFI_MODIFIED_INDEX_BASE_NAME="gufi_index_${MODIFIED_TREE_BASE_NAME}"

# --- 2. Execute the workflow ---
echo "--- Starting File Tree Comparison Workflow ---"
echo "Creating initial tree: ${ORIGINAL_TREE_NAME}"
echo "Parameters: min_depth=${TREES_MIN_DEPTH}, max_depth=${TREES_MAX_DEPTH}"

shopt -s nullglob
rm ../report/images/*.png
echo "Cleared data"
> ../report/data/metrics.txt


beforeTreeGen=${SECONDS}
python3 treeGen.py "${ORIGINAL_TREE_NAME}" "${TREES_MIN_DEPTH}" "${TREES_MAX_DEPTH}"
treeGenTime=$((SECONDS-beforeTreeGen))


echo "Initial tree created successfully."
echo ""

sleep 1

echo "Modifying the tree: ${ORIGINAL_TREE_NAME} -> ${MODIFIED_TREE_BASE_NAME}"
echo "Parameters: max_new_files=${MAX_NEW_FILES}, iterations=${ITERATIONS}"

beforeModTree=${SECONDS}
python3 modify.py "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}" "${MAX_NEW_FILES}" "${ITERATIONS}"
modTreeTime=$((SECONDS-beforeModTree))

echo "Tree modification complete. Final directory is: ${MODIFIED_TREE_BASE_NAME}$((ITERATIONS-1))"
echo ""

echo "Visualizing tree development between ${ORIGINAL_TREE_NAME} and ${MODIFIED_TREE_BASE_NAME}$((ITERATIONS-1))"
python3 visualize.py compare "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}$((ITERATIONS-1))" "${ORIGINAL_TREE_NAME}_plot.png"
echo "${ORIGINAL_TREE_NAME}_plot.png saved"
echo ""
sleep 2

echo "Creating GUFI indexes..."
echo "Creating index for original tree: ${GUFI_ORIGINAL_INDEX}"
beforeGUFIcreate=${SECONDS}
gufi_dir2index "../data/${ORIGINAL_TREE_NAME}" "../data/${GUFI_ORIGINAL_INDEX}"
echo ""
echo "Creating index for modified trees, base name: ${GUFI_MODIFIED_INDEX_BASE_NAME}"

if [ "$ITERATIONS" -gt 1 ]; then
    for ((i=0; i<ITERATIONS; i++)); do
        gufi_dir2index "../data/${MODIFIED_TREE_BASE_NAME}$i" "../data/${GUFI_MODIFIED_INDEX_BASE_NAME}$i"
        echo "GUFI index creation complete."
        echo ""
    done
else
    gufi_dir2index "$../data/{MODIFIED_TREE_BASE_NAME}0" "../data/${GUFI_MODIFIED_INDEX_BASE_NAME}0"
    echo "GUFI index creation complete."
    echo ""
fi
GUFIcreateTime=$((SECONDS-beforeGUFIcreate))


sleep 2

echo "--- Running Comparisons ---"

beforeComparison=${SECONDS}
#If there is more than one modified tree iteration
if [ "$ITERATIONS" -gt 1 ]; then
    
    echo "Comparing tree metrics and whether real file system comparisons match GUFI comparisons..."
    echo ""
    #python3 compare_trees.py "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}0"
    #python3 compare_trees.py "${GUFI_ORIGINAL_INDEX}" "${GUFI_MODIFIED_INDEX_BASE_NAME}0" --gufi
    
    #Gathering the raw file system data for comparison
    FS_Metrics=($(python3 compare_trees.py "../data/${ORIGINAL_TREE_NAME}" "../data/${MODIFIED_TREE_BASE_NAME}0" -r))

    #Gathering the raw GUFI index data for comparison
    GUFI_Metrics=($(python3 compare_trees.py "../data/${GUFI_ORIGINAL_INDEX}" "../data/${GUFI_MODIFIED_INDEX_BASE_NAME}0" --gufi -r))

    #Echo whether the metrics gathered from the FS (file system) and GUFI match or not
    #If both FS data and GUFI data match, FS data is sent to "metrics.txt"
    #Metrics data that do not match have ERROR appended and both values (FS and GUFI data) are sent to "metrics.txt"
    if [ "${FS_Metrics[*]}" == "${GUFI_Metrics[*]}" ]; then
        echo "${ORIGINAL_TREE_NAME} -> ${MODIFIED_TREE_BASE_NAME}0 : Match"
        echo "${FS_Metrics[@]}" > ../report/data/metrics.txt
    else
        echo "${ORIGINAL_TREE_NAME} -> ${MODIFIED_TREE_BASE_NAME}0 : DOES NOT MATCH"
        echo "ERROR: FS = ${FS_Metrics[@]}  GUFI = ${GUFI_Metrics[@]}" > ../report/data/metrics.txt
        for ((i=0; i<${#FS_Metrics[@]}; i++)); do
            if [ "${FS_Metrics[i]}" != "${GUFI_Metrics[i]}" ]; then
                if [ "$i" -eq 0 ]; then
                    echo -n "Tree Edit Distance: "
                elif [ "$i" -eq 1 ]; then
                    echo -n "Change in tree height: "
                elif [ "$i" -eq 2 ]; then
                    echo -n "Change in number of leaf nodes: "
                fi
                
                echo "FS = ${FS_Metrics[i]}  GUFI = ${GUFI_Metrics[i]}"
            fi
        done
        echo ""
    fi

    for ((i=1; i<ITERATIONS; i++)); do
        # To display each comparison, uncomment the two lines below
        #python3 compare_trees.py "${MODIFIED_TREE_BASE_NAME}$((i-1))" "${MODIFIED_TREE_BASE_NAME}$i"
        #python3 compare_trees.py "${GUFI_MODIFIED_INDEX_BASE_NAME}$((i-1))" "${GUFI_MODIFIED_INDEX_BASE_NAME}$i" --gufi
        
        FS_Metrics=($(python3 compare_trees.py "../data/${MODIFIED_TREE_BASE_NAME}$((i-1))" "../data/${MODIFIED_TREE_BASE_NAME}$i" -r))
        GUFI_Metrics=($(python3 compare_trees.py "../data/${GUFI_MODIFIED_INDEX_BASE_NAME}$((i-1))" "../data/${GUFI_MODIFIED_INDEX_BASE_NAME}$i" --gufi -r))

        #Echo whether the metrics gathered from the FS (file system) and GUFI match or not
        #If both FS data and GUFI data match, FS data is sent to "metrics.txt"
        #Metrics data that do not match have ERROR appended and both values (FS and GUFI data) are sent to "metrics.txt"
        if [ "${FS_Metrics[*]}" == "${GUFI_Metrics[*]}" ]; then
            echo "${MODIFIED_TREE_BASE_NAME}$((i-1)) -> ${MODIFIED_TREE_BASE_NAME}$i : Match"
            echo "${FS_Metrics[@]}" >> ../report/data/metrics.txt
        else
            echo ""
            echo "${MODIFIED_TREE_BASE_NAME}$((i-1)) -> ${MODIFIED_TREE_BASE_NAME}$i : DOES NOT MATCH"
            echo "ERROR: FS = ${FS_Metrics[@]}  GUFI = ${GUFI_Metrics[@]}" >> ../report/data/metrics.txt
            for ((j=0; j<${#FS_Metrics[@]}; j++)); do
                if [ "${FS_Metrics[j]}" != "${GUFI_Metrics[j]}" ]; then
                    if [ "$j" -eq 0 ]; then
                        echo -n "Tree Edit Distance: "
                    elif [ "$j" -eq 1 ]; then
                        echo -n "Change in tree height: "
                    elif [ "$j" -eq 2 ]; then
                        echo -n "Change in number of leaf nodes: "
                    fi
                    
                    echo "FS = ${FS_Metrics[j]}  GUFI = ${GUFI_Metrics[j]}"
                fi
            done
            echo ""
        fi

    done
else
    echo "Comparing tree metrics and whether real file system comparisons match GUFI comparisons..."
    echo ""
    # To display each comparison, uncomment the two lines below
    #python3 compare_trees.py "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}0"
    #python3 compare_trees.py "${GUFI_ORIGINAL_INDEX}" "${GUFI_MODIFIED_INDEX_BASE_NAME}0" --gufi

    #Gathering the raw file system data for comparison
    FS_Metrics=($(python3 compare_trees.py "../data/${ORIGINAL_TREE_NAME}" "../data/${MODIFIED_TREE_BASE_NAME}0" -r))

    #Gathering the raw GUFI index data for comparison
    GUFI_Metrics=($(python3 compare_trees.py "../data/${GUFI_ORIGINAL_INDEX}" "../data/${GUFI_MODIFIED_INDEX_BASE_NAME}0" --gufi -r))

    #Echo whether the metrics gathered from the FS (file system) and GUFI match or not
    #If both FS data and GUFI data match, FS data is sent to "metrics.txt"
    #Metrics data that do not match have ERROR appended and both values (FS and GUFI data) are sent to "metrics.txt"
    if [ "${FS_Metrics[*]}" == "${GUFI_Metrics[*]}" ]; then
        echo "${ORIGINAL_TREE_NAME} -> ${MODIFIED_TREE_BASE_NAME}0 : Match"
        echo "${FS_Metrics[@]}" > ../report/data/metrics.txt
    else
        echo "${ORIGINAL_TREE_NAME} -> ${MODIFIED_TREE_BASE_NAME}0 : DOES NOT MATCH"
        echo "ERROR: FS = ${FS_Metrics[@]}  GUFI = ${GUFI_Metrics[@]}" > ../report/data/metrics.txt
        for ((i=0; i<${#FS_Metrics[@]}; i++)); do
            if [ "${FS_Metrics[i]}" != "${GUFI_Metrics[i]}" ]; then
                if [ "$i" -eq 0 ]; then
                    echo -n "Tree Edit Distance: "
                elif [ "$i" -eq 1 ]; then
                    echo -n "Change in tree height: "
                elif [ "$i" -eq 2 ]; then
                    echo -n "Change in number of leaf nodes: "
                fi
                
                echo "FS = ${FS_Metrics[i]}  GUFI = ${GUFI_Metrics[i]}"
            fi
        done
    fi
    
fi
comparisonTime=$((SECONDS-beforeComparison))

echo ""
echo "--- Workflow Complete ---"
echo "   - Timing breakdown -  "
echo ""
echo "Tree creation time: $treeGenTime seconds"
echo "Tree modification time: $modTreeTime seconds"
echo "GUFI index creation time: $GUFIcreateTime seconds"
echo "Tree comparison time: $comparisonTime seconds"

# --- 3. Optional Plot Display (uncomment to enable) ---
# To automatically display a plot with the metrics data generated, uncomment the lines below.
#echo ""
#python3 plot_metrics.py




# --- 4. Optional Cleanup (uncomment to enable) ---
# To remove the generated directories and indexes, uncomment the lines below.

# Sleep command for consistency of deletion
# Fast program completion may result in leftover files/directories otherwise
echo ""
echo "Tree deletion in progress, please wait..."
sleep 3

if [ "$ITERATIONS" -gt 1 ]; then
    rm -rf "../data/${ORIGINAL_TREE_NAME}" 
    rm -rf "../data/${MODIFIED_TREE_BASE_NAME}0"

    rm -rf "../data/${GUFI_ORIGINAL_INDEX}" 
    rm -rf "../data/${GUFI_MODIFIED_INDEX_BASE_NAME}0"

    for ((i=1; i<ITERATIONS; i++)); do
        rm -rf "../data/${MODIFIED_TREE_BASE_NAME}$i"
        rm -rf "../data/${GUFI_MODIFIED_INDEX_BASE_NAME}$i"
    done
else
    rm -rf "../data/${ORIGINAL_TREE_NAME}" 
    rm -rf "../data/${MODIFIED_TREE_BASE_NAME}0"

    rm -rf "../data/${GUFI_ORIGINAL_INDEX}" 
    rm -rf "../data/${GUFI_MODIFIED_INDEX_BASE_NAME}0"
fi

echo "Tree deletion complete"

echo "Generating visuals..."
PULL_FROM_PATH="../data"
SAVE_TO_PATH="../report/images" 

echo Generating report...
python3 ../report/report_generator.py