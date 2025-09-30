import os
import shutil
from pathlib import Path
import sys

# Remove all directories with the given target_name inside base_path.
def remove_dirs(base_path):
    if os.path.exists(base_path):
        # If name is a file
        if os.path.isfile(base_path):
            print("Selected path is a file. Returning.")
            return 1
        # If name is a dir
        elif os.path.isdir(base_path):
            shutil.rmtree(base_path)

if len(sys.argv) < 2:
    print("Usage: python3 clean.py <dir_to_remove> <dirs_to_remove")
    print("If dirs_to_remove is greater than 0, it will remove dirs made with the modify.py scheme")
    sys.exit(1)

dirRemove = sys.argv[1]
recurseArg = int(sys.argv[2])

if recurseArg > 0:
    for i in range(0, recurseArg):
        remove_dirs(f"{dirRemove}{i}")

else:
    remove_dirs(dirRemove)
    