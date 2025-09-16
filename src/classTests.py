
import random
# Testing class methods in isolation



def sample_size(fileDict):
        sizeTypes = list(fileDict.keys())
        probs = [fileDict[c]["prob"] for c in sizeTypes]

        selection = random.choices(sizeTypes, weights=probs, k=1)[0]
        print(f"Picked: {selection}")

        low, high = fileDict[selection]["range"]
        size = random.randint(low, high)
        print(f"Size: {size}")
        return size


fileDictr = {
    "small" : {"range": (0, 1_000), "prob": 0.55},
    "medium" : {"range": (1_000, 1_000_000), "prob": 0.40},
    "large" : {"range": (1_000_000, 500_000_000), "prob": 0.05},
}

for i in range(0, 10):
    sizePick = sample_size(fileDictr)