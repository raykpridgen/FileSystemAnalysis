# To Do

## Standardize Setup
- requirements.txt
- script to make venv -- COMPLETE
- thorough usage statements

## Centralize workflow
### Possible structure
Generate: includes creation and modifcation
 - treeGen.py -- ADDED MORE PARAMS
 - modify.py (may be merged) -- ADDED MORE PARAMS
 - dists folder for params -- SWITCHED TO FILE

Analyze: 
 - plot_metrics.py
 - print_tree.py (outdated?)
 - tree_metrics.py
 - run_workflow.sh

Visualize:
- visualize.py -- ADDED COMPARE FEATURE
- visual.sh

GUFI:
- script for easier querying

### For each component
- Merge similar python files
- Implement classes for each functionality
- Include a main.py or shell script outside of src, that uses said classes

## Visualization

### Clarify plot output -- COMPLETE
- Clunky graph, make children centered under each parent node
- Add coloring for parent and leaf nodes?

### Future features -- COMPLETE
- Functionality that shows changes to a tree over iterations
- Color coding based on which parts have changed
- Ex: Green lines for added, red for delete, etc

# 9/30 Meeting
## Main file above src
## More specific data folder
## Future - speed of operations
## Consistent class for building a tree
 - Used in visualize and tree_metrics

# 10/7 Meeting
## Speed up compare_trees
## Add changes output from modify.py

# 10/14 - Script to centralize everythin
## Folder
### Images
- metrics
- tree visuals
### Data
- Indexes of trees
- Metrics for each tree diff
- Timings
- Authentication
### PDF Plot - Python
- arguments
- tree metrics
- GUFI functions
- Visualizations
- Graphs
- Timing

### RAG / ML Usage with GUFI

# 10/21
## LaTex Report
## Video walking through workflow
- Adress GUFI CMakeLists issues on Mac
- Standardize installation (Docker?)
### Simple, layman terms README
## Implement GUFI installation in README
