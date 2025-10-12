import matplotlib.pyplot as plt
import matplotlib.ticker as t
import statistics as s
import sys


if len(sys.argv) == 1:
    runNum = "1"
elif len(sys.argv) == 2:
    try:
        runNum = sys.argv[1]
        plt.savefig(f"../plots/plot{runNum}.png", bbox_inches='tight')
        plt.close()

    except:
        print("Usage: python3 plot_metrics.py [run_number]\nOptional run number used to number the generated plot\nDefaults to 1")



#Tree metrics must be in a file named metrics.txt
with open(f"../metrics/metrics{runNum}.txt", 'r') as file:
    content = file.readlines()

#Formatting the data
for i in range(len(content)):
    content[i] = content[i].strip()
    content[i] = content[i].split()


#Data is stored line by line in the form of: (TED) (treeHeightChange) (leafNodeNumChange)
TED = []
treeHeightChange = []
leafNodeNumChange = []
iterations = []
i = 1
for data in content:
    TED.append(int(float((data[0]))))
    treeHeightChange.append(int(data[1]))
    leafNodeNumChange.append(int(data[2]))
    iterations.append(i)
    i+=1
    


TED_stdev = s.stdev(TED)
treeHeightChange_stdev = s.stdev(treeHeightChange)
leafNodeNumChange_stdev = s.stdev(leafNodeNumChange)

average_TED = sum(TED)/len(TED)
average_treeHeightChange = sum(treeHeightChange)/len(treeHeightChange)
average_leafNodeNumChange = sum(leafNodeNumChange)/len(leafNodeNumChange)

"""
print(TED)
print(treeHeightChange)
print(leafNodeNumChange)
print("-- Standard Deviation --")
print(f"TED: {TED_stdev}")
print(f"Tree Height Change {treeHeightChange_stdev}")
print(f"Leaf Node Number Change: {leafNodeNumChange_stdev}")
"""






plt.plot(iterations, TED, label="Tree Edit Distance")
plt.plot(iterations, treeHeightChange, label="Change in tree height")
plt.plot(iterations, leafNodeNumChange, label="Change in leaf node amount")
plt.xlabel("Iterations")
plt.ylabel("Metrics")
plt.title("Change in Tree Metrics")

plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.35),
           fancybox=True, shadow=True, ncol=3)

ax = plt.gca()

# Force the x-axis to show only whole numbers
ax.xaxis.set_major_locator(t.MaxNLocator(integer=True))

# Ensure the axes are displayed, although this is the default behavior
ax.axis('on')

plt.tight_layout(rect=[0, 0.1, 1, 1])
plt.grid(True)
plt.xticks(iterations)


plt.subplots_adjust(bottom=0.45)

# Left textbox: Standard Deviation
plt.figtext(0.25, 0.1,
            "Standard Deviations\n"
            f"Tree Edit Distance: {TED_stdev:.5f}\n"
            f"Tree Height Change: {treeHeightChange_stdev:.5f}\n"
            f"Change in # of Leaf Nodes: {leafNodeNumChange_stdev:.5f}",
            fontsize=12, ha='center',
            bbox=dict(boxstyle='round,pad=0.5', fc='lightgrey', ec='k', lw=1, alpha=0.5))

# Right textbox: Averages
plt.figtext(0.75, 0.1,
            "Averages\n"
            f"Tree Edit Distance: {average_TED:.5f}\n"
            f"Tree Height Change: {average_treeHeightChange:.5f}\n"
            f"Change in # of Leaf Nodes: {average_leafNodeNumChange:.5f}",
            fontsize=12, ha='center',
            bbox=dict(boxstyle='round,pad=0.5', fc='lightblue', ec='k', lw=1, alpha=0.5))




plt.savefig(f"../plots/plot{runNum}.png", bbox_inches='tight')
plt.close()

