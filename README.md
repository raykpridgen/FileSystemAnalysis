# Prerequisite: GUFI
This project requires the [Grand Unified File Index (GUFI)](https://github.com/mar-file-system/GUFI.git) tool to be available on your system's path.

# Installation and Setup

## Recommended Method: Docker
If you do not have the GUFI tool installed locally, or you want a consistent, isolated environment, you can use Docker. This is the easiest and most reliable way to get started.

### Step 1. Install Docker
Download and install Docker Desktop onto your device. Follow the installation guide for your operating system to either install interactively or via command line.

[Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) - Requires WSL 2 backend

[Docker Desktop for macOS](https://docs.docker.com/desktop/setup/install/mac-install/) - Make sure to choose the right installer for your device (Intel chip or Apple silicon)

[Docker Desktop for Linux](https://docs.docker.com/desktop/setup/install/linux/) - After the first few steps, follow the guide for your specific distribution


After installing, verify the installation by running this command in your terminal:

`docker --version`

### Step 2. Clone the repo
`git clone https://github.com/raykpridgen/FileSystemAnalysis`

### Step 3. Move into the root directory of the repo

`cd FileSystemAnalysis`

### Step 4. Creating the Docker image
Ensure the Docker Engine is running and run this command:

`docker build -t file-system-analysis:3.13 .`

This process will take a while.

### Optional Step: Delete the repo
Once the image is successfully built, you no longer need the local repository files for execution only. However, we highly recommend keeping the local repository for simple debugging or for rebuilding the image later, should you choose to modify the source code or if your image is lost.

### Step 5. Creating the output folders
Navigate to a directory where you would like the output from our workflow to be stored and run these commands:

`mkdir -p report`

`mkdir -p data`

This command will create two directories (report and data) if they do not already exist. These folders will be linked to the corresponding report and data folders in your Docker container. Output written to these directories in the container will appear on your host machine instead.

Data will store any generated file trees. Report will store any generated text files, images, and PDF reports.

These links must be established every time you run the container via the docker run command provided in the next step.

### Step 6. Launching the Container's Command Line Interface
To access the command line interface in the container, run this command:

`docker run -it --rm -v "$(pwd)/report":/app/report -v "$(pwd)/data":/app/data file-system-analysis:3.13 /bin/bash`

Here, you can execute the scripts in our workflow. To exit the container, enter the command:

`exit`

## Alternate Method: Local Setup

If you want to run the workflow directly on your host machine:

### Step 1. Clone the repo
`git clone https://github.com/raykpridgen/FileSystemAnalysis`

### Step 2. Move into the src directory
`cd FileSystemAnalysis/src`

### Step 3. Clone the GUFI repo
`mkdir gufi && cd gufi && git clone https://github.com/mar-file-system/GUFI` 

After this is cloned, please follow the setup instructions within the GUFI readme to set up GUFI.

### Step 4. Create a virtual environment

To create a virtual environment with all necessary dependencies to run our workflow, run this command:

`./make_venv.sh`

### Step 5. Activate your virtual environment

While still in the src directory, run this command to activate the virtual environment:

`source ../../venv/bin/activate`

If activated successfully, you should see (venv) at the beginning of your terminal prompt before your username or current path.

When restarting your terminal instance, you will have to activate your virtual environment again.

# Quick start
## Run this to utilize pre-built workflow
`./run_workflow.sh 10 5 10`

- A report will be generated in /reports

# Generating Filesystem Trees
treeGen.py is the script used to generate trees, located in the /src folder. This will generate a psuedorandom file tree using probabilities in JSON and input parameters. Commandline arguments are as follows:

## To generate a new tree in the /data folder
`python3 treeGen.py <name_of_root_directory> <minimum_depth> <maximum_depth>`

## Remove tree(s)
`python3 treeGen.py clean <root_name> <number_of_trees_to_remove>`

- If the number is set to 0, it will only remove 1 dir associated with the name passed.


# Modifying Filesystem Trees
modify.py operates on an existing filesystem tree, modeling psuedorandom changes to a tree in time steps. This script may add, delete, or change files, folders, and symlinks based on probabilities provided via JSON.

`python3 modify.py <original_name> <modified_name> <max_new_files> <iterations>`

- First two inputs are the root to edit, and the name of the root to place the modified tree in
- max_new_files is the maximum number of files modify.py will add to the tree
- Iterations determines how many times this process will repeat. It will iterate using the same process, running a further iteration on the newly generated tree. 


# Generating GUFI Indexes
To generate a GUFI index of a file system tree, run this command:

`gufi_dir2index [root] [GUFIroot]`

The root argument is the starting directory of the file system tree. The resulting GUFI index will then use the GUFIroot argument as its own newly defined starting directory.

# Gathering Metrics Data
compare_trees.py takes in the two starting directories for your trees and gathers metrics which it then uses to compare the two trees.
Metrics gathered: tree edit distance, change in tree height, change in number of leaf nodes (nodes with no children).

To plot the data using plot_metrics.py, use the -r flag to generate raw numerical data (without any descriptive text for the user) and then specify the path to where the text file with the data should be generated.

## To compare two trees:
For file system trees:

`python3 compare_trees.py <directory1> <directory2>`

For GUFI indexes:

`python3 compare_trees.py <GUFI_index1> <GUFI_index2> --gufi`

## To print the raw numerical data to the terminal:
For file system trees:

`python3 compare_trees.py <directory1> <directory2> -r`

For GUFI indexes:

`python3 compare_trees.py <GUFI_index1> <GUFI_index2> --gufi -r`

## To send the raw numerical data to a text file compatible with plot_metrics.py:
For file system trees:

`python3 compare_trees.py <directory1> <directory2> -r <text_file_path>`

For GUFI indexes:

`python3 compare_trees.py <GUFI_index1> <GUFI_index2> --gufi -r <text_file_path>`

# Tree Creation Debugging
print_tree.py will display one or two trees for debugging purposes.

For file system trees:

`python3 print_tree.py <root> [root2]`

For GUFI indexes:

`python3 print_tree.py <GUFI_index> [GUFI_index2] --gufi`

# Plotting the metrics data

plot_metrics.py takes in multiple iterations of the raw numerical data generated by compare_trees.py and plots the data for the user in a PNG file. Averages and standard deviation are also generated and displayed in the PNG file.

`python3 plot_metrics.py <metrics_text_file>`

The metrics_text_file argument is the path to the file generated by compare_trees.py

# Running the Workflow
run_workflow.sh is a script that automates the tree creation and comparison process. A detailed report is generated in the report directory, located next to the src directory.

`./run_workflow.sh <iterations> <min_tree_depth> <max_tree_depth>`

The iterations, min_tree_depth and max_tree_depth arguments are passed to modify.py in the script, determining how many tree modifications take place, the minimum depth of the generated trees, and the maximum depth of the generated trees. Must be integers greater than or equal to 1.
 

To simply clean the report directory, run:

`./run_workflow.sh clean`
