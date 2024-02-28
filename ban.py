# ban - backup analyzer
# Given two files with a format
#   <checksum> <file path>
# Will output:
#  1. Checksums and their file paths that are present in the first file but not in the second one

import sys

class Entry:
    """Represents an entry from an input file"""
    def __init__(self, sha, path):
        self.sha = sha
        self.path = path

    def getSha(self):
        return self.sha

    def getPath(self):
        return self.path

if len(sys.argv) != 3:
    print("Incorrect usage, specify two files!")
    sys.exit(1)

def readEntries(fileHandle):
    entries = []

    while True:
        line = fileHandle.readline()
        if not line:
            return entries

        sha = line[:64]
        path = line[66:-1]
        entry = Entry(sha, path)

        entries.append(entry)

def listToDict(listOfEntries):
    dic = {}
    for entry in listOfEntries:
        if entry.getSha() in dic:
            dic[entry.getSha()].append(entry.getPath())
        else:
            dic[entry.getSha()] = [entry.getPath()]
    return dic

oldBackup = sys.argv[1]
newBackup = sys.argv[2]

print("old backup: " + oldBackup + ", new backup: " + newBackup)

oldEntries = []
newEntries = []

with open(oldBackup) as ob:
    oldEntries = readEntries(ob)

with open(newBackup) as nb:
    newEntries = readEntries(nb)

print("old entries: " + str(len(oldEntries)) + ", new entries: " + str(len(newEntries)))

# Create a dictionary of entries
oldHashMap = listToDict(oldEntries)
newHashMap = listToDict(newEntries)

# Find entries that are present in the old dictionary, but are missing in the second one:
for sha in oldHashMap:
    if not sha in newHashMap:
        print(sha + " " + str(oldHashMap[sha]))

# Find entries that are duplicate within old file and print them out
def findDupeHashes(dic):
    for sha in dic:
        if len(dic[sha]) > 1:
            for path in dic[sha]:
                print("+ " + path)
            print("")
