# Metrics to Analyze Trees with

## Tree Analysis

### Height / Depth
- Distance from root to leaf
- Average
- Maximum

### Degree
- Number of children a node has
- Average
- Maximum

### Size 
- Total number of nodes

### Balance
- How even branches are distributed

## Filesystem Specific

### File Count / Folder Count Ratio

### File Size Distribution
- Min / Max
- Average
- Variance of file sizes

### Storage Depth Distribution
- Where files tend to live
- Shallow or deep

### Largest Subtree
- Whiuch folder has the most descendants
- Which folder has the most bytes

## Traversal and Efficiency Metrics

### Path Length
- Sum of all root to node distances

### Average Path Length
- Navigation cost

### Node density per level
- Nodes at each depth
- Good for tree shape

## Customizable Metrics

### Change node weights
- weight by file size

### Thresholds
- Flag folders deeper than N
- Flag folders bigger than M MB


gufi_query edit before paste



# Permissions scheme
"""
Owner | Group | Others
r w x   r w x   r w x

r = 4
w = 2 
x = 1

Sum bits for each category

"""

# Basic params / structure for generation
"""
Attrs to model for GUFI

name
- vary name length?

type
- Regular files, dirs, symlinks, sockets/pipes
- extentions tied to size expectations

uid
- Pick from a pool of users, assign distributions to each user
gid
- set random groups?

size
- distribution param (many small + few big, etc)

access time
mod time
creation time
status change time
- FOR TIMES: crtime <= ctime <= mtime <= atime
- allow random but do not deviate from scheme, for logical creation
"""

# Use cases from GUFI
"""
- entry queries: find recently accessed files
- dir summaries: size, count, etc
- tree-summary: Full tree rollup

"""