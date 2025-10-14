import time

def getTimeInMs(startTime, endTime):
    returnTime = (endTime - startTime) * 1000
    return f"{returnTime:.2f}"