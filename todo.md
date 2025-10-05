# To Do

## Standardize Setup
- requirements.txt
- script to make venv?
- thorough usage statements

## Centralize workflow
### Possible structure
Generate: includes creation and modifcation
 - treeGen.py
 - modify.py (may be merged)
 - dists folder for params

Analyze: 
 - plot_metrics.py
 - print_tree.py (outdated?)
 - tree_metrics.py
 - run_workflow.sh

Visualize:
- visualize.py
- visual.sh

GUFI:
- script for easier querying

### For each component
- Merge similar python files
- Implement classes for each functionality
- Include a main.py or shell script outside of src, that uses said classes

## Visualization

### Clarify plot output
- Clunky graph, make children centered under each parent node
- Add coloring for parent and leaf nodes?

### Future features
- Functionality that shows changes to a tree over iterations
- Color coding based on which parts have changed
- Ex: Green lines for added, red for delete, etc

# 9/30 Meeting
## Main file above src
## More specific data folder
## Future - speed of operations
## Consistent class for building a tree
 - Used in visualize and tree_metrics