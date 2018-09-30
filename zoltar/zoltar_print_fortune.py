import random

# max number of characters allowed per line
MAX_CHARACTER_LIMIT = 28;

# a function return an array that tells the index of all spaces in the string
def findSpaces(s):
    return [i for i, ltr in enumerate(s) if ltr == ' ']

# read all fortunes from the fortunes.txt file in this directory
# split by newline
fortunes = open('./fortunes.txt').read().splitlines()
# picking a fortune string at random
fortune = random.choice(fortunes)

# Whichever fortune we pick, we need to 
# 1) prepend with a space for consistency with the splitting algorithm
# 2) prepend with a phrase of our choosing for the fortune
# 3) postpend with a space for algorithm splitting
fortune = ' ' + 'Zoltar says: ' + fortune + ' '

# initialize a queue to print out
queue = []

# if our fortune is under 30 characters, we're okay to just send it through
if len(fortune) <= MAX_CHARACTER_LIMIT:
    spaceIndexes = -1
    queue = [ fortune ] 
else:
    spaceIndexes = findSpaces(fortune)

# an in memory value to keep ahold of the last split
lastSplitIdx = -1;

# if it's greater than -1, we need to perform iteration through the string
if spaceIndexes > -1:
    # get both the index and value of item
    for idx,value in enumerate(spaceIndexes):
        # check to see if the value is greater than 40 times the current offset
        if value > MAX_CHARACTER_LIMIT * ( len(queue) + 1 ): 
            # for the first one to exceed 40, we want the one BEFORE it
            # we start at 0 for now
            startIdx = 0
            # we end at idx - 1
            endIdx = spaceIndexes[idx-1]
            # if lastSplitIdx is NOT -1, it has been assigned, so let's use that
            if lastSplitIdx != -1:
                startIdx = spaceIndexes[lastSplitIdx]

            element = fortune[startIdx:endIdx]
            # assign lastSplitIdx for next iteration
            lastSplitIdx = idx - 1
            # push to the queue
            queue.append(element)
    # we are now done with our for loop, but to ensure we got the WHOLE message,
    # we want to see if lastSplitIdx equals the last index of enumerate(spaceIndexes)
    # if they DON'T equal, we want to append the rest of our message
    if spaceIndexes[lastSplitIdx] != spaceIndexes[-1]:
        # start at the lastSplitIdx
        startIdx = spaceIndexes[lastSplitIdx]
        # go from the startIdx to the end
        element = fortune[startIdx:]
        # push to queue
        queue.append(element)


# ADAFRUIT INITIALIZATION

from Adafruit_Thermal import *
# grab printer
printer = Adafruit_Thermal("/dev/serial0", 19200, timeout=5)

printer.feed(1)      # whitespace at the top of the print
printer.justify('C') # justify center 
printer.setSize('M') # Mid size text
printer.boldOn()     # bold the text in this

# from our built queue array, go through and print each line.
for element in queue:
    printer.println(element)

printer.boldOff()    # remove the bold
printer.feed(5)      # whitespace at the bottom of the print
printer.sleep()      # Tell printer to sleep
printer.wake()       # Call wake() before printing again, even if reset
printer.setDefault() # Restore printer to defaults