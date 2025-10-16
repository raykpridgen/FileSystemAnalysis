from treeGen import ArtificialTree
from modify import ModifyTree
import os
from pathlib import Path
from utils import parse_dist_params, parse_edit_params
# Clear screen based on OS
def clear_screen():
    if os.name == "nt":  # Windows
        os.system("cls")
    else:                # macOS / Linux / WSL
        os.system("clear")

if __name__ == "__main__":
    running = True

    while running:
        clear_screen()
        dataPath = Path("../data/")
        print("\n=== Filesystem Analysis ===")
        print("1. List generated trees")
        print("2. Generate new tree")
        print("3. Modify existing tree")
        print("4. Generate plot of tree(s)")
        print("5. View plots")
        print("6. Quit")

        choice = input("Enter: ")

        # Print trees made
        if choice == "1":
            print("\n")
            for entry in dataPath.iterdir():
                print(f": {str(entry)[8:]}\n")

            input("")

        # Generate new tree
        elif choice == "2":
            rootName = input("Enter root name: ")
            minDepth = input("Enter minimum depth: ")
            maxDepth = input("Enter maximum depth: ")
            degDist, FTdist, FEdist, PMdist, sizeDist = parse_dist_params()
    


        elif choice == "3":
            # Simulated user-entered message
            message = "Hello, world!"  # pretend user typed this
            print(f"\n[Option 3 Selected]")
            print(f"Simulated input message: {message}")

        elif choice == "4":
            print("\nExiting the menu. Goodbye!")
            running = False

        else:
            print("\nInvalid choice. Please enter a number from 1 to 4.")
