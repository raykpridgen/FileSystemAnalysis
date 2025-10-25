#!/bin/bash

# =================================================================
# This script automates the full file tree comparison workflow.
# =================================================================

mkdir -p ../data
mkdir -p ../report/data
mkdir -p ../report/images

# --- Set up Date Command for Millisecond Portability ---

cross_platform_date() {
    # Attempt to run date with millisecond format (%3N)
    local MILLISECONDS_FORMAT="+%s%3N"
    local output=$(date "$MILLISECONDS_FORMAT" 2>/dev/null)
    
    # Check if the output contains the literal format string.
    # This indicates that the 'date' utility did not recognize %N.
    # We check for the format string itself, or the trailing 'N'.
    if [[ "$output" == *"%N"* ]] || [[ "$output" =~ [0-9]+N$ ]]; then
        # Fallback to seconds-only precision (BSD 'date' compatible)
        date "+%s"
    else
        # Millisecond format worked (e.g., Linux or gdate is in use)
        echo "$output"
    fi
}

get_date_precision() {
    local MILLISECONDS_FORMAT="+%s%3N"
    local test_output=$(date "$MILLISECONDS_FORMAT" 2>/dev/null)
    
    # Check for the failure marker (literal format string parts)
    if [[ "$test_output" == *"%N"* ]] || [[ "$test_output" =~ [0-9]+N$ ]]; then
        echo "seconds"
    else
        echo "milliseconds"
    fi
}

check_and_warn_on_fallback() {
    local MILLISECONDS_FORMAT="+%s%3N"
    local test_output=$(date "$MILLISECONDS_FORMAT" 2>/dev/null)
    
    # Check for the failure marker (literal format string parts)
    if [[ "$test_output" == *"%N"* ]] || [[ "$test_output" =~ [0-9]+N$ ]]; then
        echo ""
        echo "WARNING: 'date' utility lacks millisecond support. Falling back to seconds."
        echo "For millisecond precision, ensure you have a version of 'date' from GNU Coreutils installed." 1>&2
    fi
}


DATE_PRECISION=$(get_date_precision)


param=$1
MIN_DEPTH=$2
MAX_DEPTH=$3
# If first param is not clean, and the params are not positive integers, print usage
if [[ "$param" != "clean" ]] && \
    [[ ! "$param" =~ ^[1-9][0-9]*$ || ! "$MIN_DEPTH" =~ ^[1-9][0-9]*$ || ! "$MAX_DEPTH" =~ ^[1-9][0-9]*$ ]]; then
    echo ""
    echo ""
    echo "This program automates usage for all major executions in this project, found in the src folder."
    echo " -- Usage is expected for generating, modifying, plotting, and generating a report for a filesystem tree."
    echo ""
    echo "To execute this program, run:"
    echo "    $0 <iterations> <min_tree_depth> <max_tree_depth>"
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
    > ../report/data/timing.txt
    > ../report/data/parameters.txt
    echo "Cleared data"
    exit 0
fi
# --- 1. Define filenames and parameters ---

ORIGINAL_TREE_NAME="original_tree"
MODIFIED_TREE_BASE_NAME="modified_tree"
ITERATIONS=$param


# Generate random parameters for trees.py
# Depth and Degree
TREES_MIN_DEPTH=$MIN_DEPTH
TREES_MAX_DEPTH=$MAX_DEPTH

# Generate random parameters for modify.py
# Max new files (0 - 3)
MAX_NEW_FILES=$(( 20 ))




# Define GUFI index names
GUFI_ORIGINAL_INDEX="gufi_index_${ORIGINAL_TREE_NAME}"
GUFI_MODIFIED_INDEX_BASE_NAME="gufi_index_${MODIFIED_TREE_BASE_NAME}"

# --- 2. Execute the workflow ---
echo "--- Starting File Tree Comparison Workflow ---"
echo "Creating initial tree: ${ORIGINAL_TREE_NAME}"
echo "Parameters: min_depth=${TREES_MIN_DEPTH}, max_depth=${TREES_MAX_DEPTH}"

shopt -s nullglob
rm ../report/images/*.png
rm ../report/final_report.pdf
rm -rf ../data && mkdir ../data
sleep 1
> ../report/data/metrics.txt
> ../report/data/timing.txt
> ../report/data/parameters.txt
echo "Cleared data"

beforeTreeGen=$(cross_platform_date)
python3 treeGen.py "${ORIGINAL_TREE_NAME}" "${TREES_MIN_DEPTH}" "${TREES_MAX_DEPTH}"
afterTreeGen=$(cross_platform_date)
treeGenTime=$((afterTreeGen - beforeTreeGen))


echo "Initial tree created successfully."
echo ""

sleep 1

echo "Modifying the tree: ${ORIGINAL_TREE_NAME} -> ${MODIFIED_TREE_BASE_NAME}"
echo "Parameters: max_new_files=${MAX_NEW_FILES}, iterations=${ITERATIONS}"

beforeModTree=$(cross_platform_date)
python3 modify.py "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}" "${MAX_NEW_FILES}" "${ITERATIONS}"
afterModTree=$(cross_platform_date)
modTreeTime=$((afterModTree - beforeModTree))

echo "Tree modification complete. Final directory is: ${MODIFIED_TREE_BASE_NAME}$((ITERATIONS-1))"
echo ""

#echo "Visualizing tree development between ${ORIGINAL_TREE_NAME} and ${MODIFIED_TREE_BASE_NAME}$((ITERATIONS-1))"
#python3 visualize.py compare "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}$((ITERATIONS-1))" "${ORIGINAL_TREE_NAME}_plot.png"
#echo "${ORIGINAL_TREE_NAME}_plot.png saved"
#echo ""
sleep 2

echo "Creating GUFI indexes..."
echo "Creating index for original tree: ${GUFI_ORIGINAL_INDEX}"
beforeGUFIcreate=$(cross_platform_date)
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
    gufi_dir2index "../data/${MODIFIED_TREE_BASE_NAME}0" "../data/${GUFI_MODIFIED_INDEX_BASE_NAME}0"
    echo "GUFI index creation complete."
    echo ""
fi

afterGUFIcreate=$(cross_platform_date)
GUFIcreateTime=$((afterGUFIcreate - beforeGUFIcreate))

sleep 2

echo "--- Running Comparisons ---"

beforeComparison=$(cross_platform_date)
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

        python3 visualize.py compare "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}0" "0:${ORIGINAL_TREE_NAME}-to-${MODIFIED_TREE_BASE_NAME}0.png"

        
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
            python3 visualize.py compare "${MODIFIED_TREE_BASE_NAME}$((i-1))" "${MODIFIED_TREE_BASE_NAME}${i}" "${i}:${MODIFIED_TREE_BASE_NAME}$((i-1))-to-${MODIFIED_TREE_BASE_NAME}${i}.png"
            

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

    #half=$(( (ITERATIONS + 1) / 2 ))  # integer division
    #last=$((ITERATIONS - 1))
    #python3 visualize.py compare "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}${half}" "${half}:${ORIGINAL_TREE_NAME}-to-${MODIFIED_TREE_BASE_NAME}.png"
    #python3 visualize.py compare "${MODIFIED_TREE_BASE_NAME}${half}" "${MODIFIED_TREE_BASE_NAME}${last}" "${last}:${MODIFIED_TREE_BASE_NAME}${half}-to-${MODIFIED_TREE_BASE_NAME}.png"

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

        python3 visualize.py compare "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}0" "1:${ORIGINAL_TREE_NAME}-to-${MODIFIED_TREE_BASE_NAME}0.png"

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

afterComparison=$(cross_platform_date)
comparisonTime=$((afterComparison - beforeComparison))

echo ""
echo "--- Workflow Complete ---"
echo "   - Timing breakdown -  "
check_and_warn_on_fallback
echo ""
echo "Tree creation time: $treeGenTime $DATE_PRECISION" | tee ../report/data/timing.txt
echo "Tree modification time: $modTreeTime $DATE_PRECISION" | tee -a ../report/data/timing.txt
echo "GUFI index creation time: $GUFIcreateTime $DATE_PRECISION" | tee -a ../report/data/timing.txt
echo "Tree comparison time: $comparisonTime $DATE_PRECISION" | tee -a ../report/data/timing.txt



echo ""
echo "Generating visuals..."
python3 plot_metrics.py ../report/data/metrics.txt
PULL_FROM_PATH="../data"
SAVE_TO_PATH="../report/images" 

echo Generating report...
python3 report_generator.py