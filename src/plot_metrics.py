import matplotlib.pyplot as plt
import matplotlib.ticker as t

#Tree metrics must be in a file named metrics.txt

with open('metrics.txt', 'r') as file:
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
    


print(TED)
print(treeHeightChange)
print(leafNodeNumChange)


plt.plot(iterations, TED, label="Tree Edit Distance")
plt.plot(iterations, treeHeightChange, label="Change in tree height")
plt.plot(iterations, leafNodeNumChange, label="Change in leaf node amount")
plt.xlabel("Iterations")
plt.ylabel("Metrics")
plt.title("Change in Tree Metrics")

plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), fancybox=True, shadow=True, ncol=3)

ax = plt.gca()

# Force the x-axis to show only whole numbers
ax.xaxis.set_major_locator(t.MaxNLocator(integer=True))

# Ensure the axes are displayed, although this is the default behavior
ax.axis('on')

plt.tight_layout(rect=[0, 0.1, 1, 1])

plt.show()