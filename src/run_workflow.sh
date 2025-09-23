#!/bin/bash

# =================================================================
# This script automates the full file tree comparison workflow.
# =================================================================

# --- 1. Define filenames and parameters ---

ORIGINAL_TREE_NAME="original_tree"
MODIFIED_TREE_BASE_NAME="modified_tree"

# Generate random parameters for trees.py
# Depth (1-4) and Degree (2-8)
TREES_DEPTH=$(( RANDOM % 4 + 1 ))
TREES_DEGREE=$(( RANDOM % 7 + 2 ))

# Generate random parameters for modify.py
# Max new files (3-5), and probabilities (0.1-0.5)
MAX_NEW_FILES=$(( RANDOM % 3 + 3 ))
DELETE_PROB=$(awk 'BEGIN{srand(); printf "%.2f\n", (rand() * 0.4 + 0.1)}')
EDIT_PROB=$(awk 'BEGIN{srand(); printf "%.2f\n", (rand() * 0.4 + 0.1)}')
CREATE_PROB=$(awk 'BEGIN{srand(); printf "%.2f\n", (rand() * 0.4 + 0.1)}')
# Hardcode iterations to 1
ITERATIONS=1

# Determine the name of the final modified tree
# The modify.py script appends the iteration number without an underscore.
LAST_ITERATION=$((ITERATIONS - 1))
FINAL_MODIFIED_TREE_NAME="${MODIFIED_TREE_BASE_NAME}${LAST_ITERATION}"

# Define GUFI index names
GUFI_ORIGINAL_INDEX="gufi_index_${ORIGINAL_TREE_NAME}"
GUFI_MODIFIED_INDEX="gufi_index_${FINAL_MODIFIED_TREE_NAME}"


# --- 2. Execute the workflow ---
echo "--- Starting File Tree Comparison Workflow ---"
echo "Creating initial tree: ${ORIGINAL_TREE_NAME}"
echo "Parameters: depth=${TREES_DEPTH}, degree=${TREES_DEGREE}"
python3 trees.py "${ORIGINAL_TREE_NAME}" "${TREES_DEPTH}" "${TREES_DEGREE}"
echo "Initial tree created successfully."
echo ""

echo "Modifying the tree: ${ORIGINAL_TREE_NAME} -> ${FINAL_MODIFIED_TREE_NAME}"
echo "Parameters: max_new_files=${MAX_NEW_FILES}, delete_prob=${DELETE_PROB}, edit_prob=${EDIT_PROB}, create_prob=${CREATE_PROB}, iterations=${ITERATIONS}"
python3 modify.py "${ORIGINAL_TREE_NAME}" "${MODIFIED_TREE_BASE_NAME}" "${MAX_NEW_FILES}" "${DELETE_PROB}" "${EDIT_PROB}" "${CREATE_PROB}" "${ITERATIONS}"
echo "Tree modification complete. Final directory is: ${FINAL_MODIFIED_TREE_NAME}"
echo ""

echo "Creating GUFI indexes for both trees..."
echo "Creating index for original tree: ${GUFI_ORIGINAL_INDEX}"
gufi_dir2index "${ORIGINAL_TREE_NAME}" "${GUFI_ORIGINAL_INDEX}"
echo "Creating index for modified tree: ${GUFI_MODIFIED_INDEX}"
gufi_dir2index "${FINAL_MODIFIED_TREE_NAME}" "${GUFI_MODIFIED_INDEX}"
echo "GUFI index creation complete."
echo ""

echo "--- Running Comparisons ---"
echo "Comparing file system trees..."
python3 compare_trees.py "${ORIGINAL_TREE_NAME}" "${FINAL_MODIFIED_TREE_NAME}"
echo ""

echo "Comparing GUFI indexes..."
python3 compare_trees.py "${GUFI_ORIGINAL_INDEX}" "${GUFI_MODIFIED_INDEX}" --gufi
echo ""

echo "--- Workflow Complete ---"


# --- 3. Optional Cleanup (uncomment to enable) ---
# To remove the generated directories and indexes, uncomment the lines below.
python3 clean.py "${ORIGINAL_TREE_NAME}" 0
python3 clean.py "${FINAL_MODIFIED_TREE_NAME}" 0
rm -rf "${GUFI_ORIGINAL_INDEX}"
rm -rf "${GUFI_MODIFIED_INDEX}"
