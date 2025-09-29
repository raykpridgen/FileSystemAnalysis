#!/bin/bash

# =================================================================
# This script automates the full file tree comparison workflow.
# =================================================================

# --- 1. Define filenames and parameters ---

ORIGINAL_TREE_NAME="original_tree"
MODIFIED_TREE_BASE_NAME="modified_tree"

# Generate random parameters for trees.py
# Depth and Degree
TREES_DEPTH=$(( RANDOM % 3 + 1 ))
TREES_DEGREE=$(( RANDOM % 3 + 2 ))

# Generate random parameters for modify.py
# Max new files (3-5), and probabilities (0.1-0.5)
MAX_NEW_FILES=$(( RANDOM % 10 ))
DELETE_PROB=$(awk 'BEGIN{srand(); printf "%.2f\n", (rand() * 0.4 + 0.1)}')
EDIT_PROB=$(awk 'BEGIN{srand(); printf "%.2f\n", (rand() * 0.4 + 0.1)}')
CREATE_PROB=$(awk 'BEGIN{srand(); printf "%.2f\n", (rand() * 0.4 + 0.1)}')

# Hardcode iterations for testing purposes
ITERATIONS=5

# Define GUFI index names
GUFI_ORIGINAL_INDEX="gufi_index_${ORIGINAL_TREE_NAME}"
GUFI_MODIFIED_INDEX_BASE_NAME="gufi_index_${MODIFIED_TREE_BASE_NAME}"






# --- 2. Execute the workflow ---
echo "--- Starting File Tree Comparison Workflow ---"
echo "Creating initial tree: ${ORIGINAL_TREE_NAME}"
echo "Parameters: depth=${TREES_DEPTH}, degree=${TREES_DEGREE}"

beforeTreeGen=${SECONDS}
python3 trees.py "${ORIGINAL_TREE_NAME}" "${TREES_DEPTH}" "${TREES_DEGREE}"
treeGenTime=$((SECONDS-beforeTreeGen))


echo "Initial tree created successfully."
echo ""


echo "Modifying the tree: ${ORIGINAL_TREE_NAME} -> ${MODIFIED_TREE_BASE_NAME}"
echo "Parameters: max_new_files=${MAX_NEW_FILES}, delete_prob=${DELETE_PROB}, edit_prob=${EDIT_PROB}, create_prob=${CREATE_PROB}, iterations=${ITERATIONS}"

beforeModTree=${SECONDS}
python3 modify.py "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}" "${MAX_NEW_FILES}" "${DELETE_PROB}" "${EDIT_PROB}" "${CREATE_PROB}" "${ITERATIONS}"
modTreeTime=$((SECONDS-beforeModTree))

echo "Tree modification complete. Final directory is: ${MODIFIED_TREE_BASE_NAME}$((ITERATIONS-1))"
echo ""


echo "Creating GUFI indexes..."
echo "Creating index for original tree: ${GUFI_ORIGINAL_INDEX}"
beforeGUFIcreate=${SECONDS}
gufi_dir2index "${ORIGINAL_TREE_NAME}" "${GUFI_ORIGINAL_INDEX}"
echo ""
echo "Creating index for modified trees, base name: ${GUFI_MODIFIED_INDEX_BASE_NAME}"

if [ "$ITERATIONS" -gt 1 ]; then
    for ((i=0; i<ITERATIONS; i++)); do
        gufi_dir2index "${MODIFIED_TREE_BASE_NAME}$i" "${GUFI_MODIFIED_INDEX_BASE_NAME}$i"
        echo "GUFI index creation complete."
        echo ""
    done
else
    gufi_dir2index "${MODIFIED_TREE_BASE_NAME}0" "${GUFI_MODIFIED_INDEX_BASE_NAME}0"
    echo "GUFI index creation complete."
    echo ""
fi
GUFIcreateTime=$((SECONDS-beforeGUFIcreate))




echo "--- Running Comparisons ---"

beforeComparison=${SECONDS}
#If there is more than one modified tree iteration
if [ "$ITERATIONS" -gt 1 ]; then
    
    echo "Comparing tree metrics and whether real file system comparisons match GUFI comparisons..."
    echo ""
    #python3 compare_trees.py "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}0"
    #python3 compare_trees.py "${GUFI_ORIGINAL_INDEX}" "${GUFI_MODIFIED_INDEX_BASE_NAME}0" --gufi
    
    #Gathering the raw file system data for comparison
    FS_Metrics=($(python3 compare_trees.py "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}0" -r))

    #Gathering the raw GUFI index data for comparison
    GUFI_Metrics=($(python3 compare_trees.py "${GUFI_ORIGINAL_INDEX}" "${GUFI_MODIFIED_INDEX_BASE_NAME}0" --gufi -r))

    #Echo whether the metrics gathered from the FS (file system) and GUFI match or not
    #If both FS data and GUFI data match, FS data is sent to "metrics.txt"
    #Metrics data that do not match have ERROR appended and both values (FS and GUFI data) are sent to "metrics.txt"
    if [ "${FS_Metrics[*]}" == "${GUFI_Metrics[*]}" ]; then
        echo "${ORIGINAL_TREE_NAME} -> ${MODIFIED_TREE_BASE_NAME}0 : Match"
        echo "${FS_Metrics[@]}" > metrics.txt
    else
        echo "${ORIGINAL_TREE_NAME} -> ${MODIFIED_TREE_BASE_NAME}0 : DOES NOT MATCH"
        echo "ERROR: FS = ${FS_Metrics[@]}  GUFI = ${GUFI_Metrics[@]}" > metrics.txt
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
        
        FS_Metrics=($(python3 compare_trees.py "${MODIFIED_TREE_BASE_NAME}$((i-1))" "${MODIFIED_TREE_BASE_NAME}$i" -r))
        GUFI_Metrics=($(python3 compare_trees.py "${GUFI_MODIFIED_INDEX_BASE_NAME}$((i-1))" "${GUFI_MODIFIED_INDEX_BASE_NAME}$i" --gufi -r))

        #Echo whether the metrics gathered from the FS (file system) and GUFI match or not
        #If both FS data and GUFI data match, FS data is sent to "metrics.txt"
        #Metrics data that do not match have ERROR appended and both values (FS and GUFI data) are sent to "metrics.txt"
        if [ "${FS_Metrics[*]}" == "${GUFI_Metrics[*]}" ]; then
            echo "${MODIFIED_TREE_BASE_NAME}$((i-1)) -> ${MODIFIED_TREE_BASE_NAME}$i : Match"
            echo "${FS_Metrics[@]}" >> metrics.txt
        else
            echo ""
            echo "${MODIFIED_TREE_BASE_NAME}$((i-1)) -> ${MODIFIED_TREE_BASE_NAME}$i : DOES NOT MATCH"
            echo "ERROR: FS = ${FS_Metrics[@]}  GUFI = ${GUFI_Metrics[@]}" >> metrics.txt
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
    FS_Metrics=($(python3 compare_trees.py "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}0" -r))

    #Gathering the raw GUFI index data for comparison
    GUFI_Metrics=($(python3 compare_trees.py "${GUFI_ORIGINAL_INDEX}" "${GUFI_MODIFIED_INDEX_BASE_NAME}0" --gufi -r))

    #Echo whether the metrics gathered from the FS (file system) and GUFI match or not
    #If both FS data and GUFI data match, FS data is sent to "metrics.txt"
    #Metrics data that do not match have ERROR appended and both values (FS and GUFI data) are sent to "metrics.txt"
    if [ "${FS_Metrics[*]}" == "${GUFI_Metrics[*]}" ]; then
        echo "${ORIGINAL_TREE_NAME} -> ${MODIFIED_TREE_BASE_NAME}0 : Match"
        echo "${FS_Metrics[@]}" > metrics.txt
    else
        echo "${ORIGINAL_TREE_NAME} -> ${MODIFIED_TREE_BASE_NAME}0 : DOES NOT MATCH"
        echo "ERROR: FS = ${FS_Metrics[@]}  GUFI = ${GUFI_Metrics[@]}" > metrics.txt
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
echo ""
python3 plot_metrics.py




# --- 4. Optional Cleanup (uncomment to enable) ---
# To remove the generated directories and indexes, uncomment the lines below.

# Sleep command for consistency of deletion
# Fast program completion may result in leftover files/directories otherwise
echo ""
echo "Tree deletion in progress, please wait..."
sleep 2

if [ "$ITERATIONS" -gt 1 ]; then
    rm -rf "${ORIGINAL_TREE_NAME}" 
    rm -rf "${MODIFIED_TREE_BASE_NAME}0"

    rm -rf "${GUFI_ORIGINAL_INDEX}" 
    rm -rf "${GUFI_MODIFIED_INDEX_BASE_NAME}0"

    for ((i=1; i<ITERATIONS; i++)); do
        rm -rf "${MODIFIED_TREE_BASE_NAME}$i"
        rm -rf "${GUFI_MODIFIED_INDEX_BASE_NAME}$i"
    done
else
    rm -rf "${ORIGINAL_TREE_NAME}" 
    rm -rf "${MODIFIED_TREE_BASE_NAME}0"

    rm -rf "${GUFI_ORIGINAL_INDEX}" 
    rm -rf "${GUFI_MODIFIED_INDEX_BASE_NAME}0"
fi

echo "Tree deletion complete"