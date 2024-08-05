# ban - backup analyzer
# Given two files with a format
#   <checksum> <file path>
# Will output:
#  1. Checksums and their file paths that are present in the first file but not in the second one

import sys
import logging



class entry:
    """Represents an entry from an input file"""
    def __init__(self, sha, path):
        self.sha = sha
        self.path = path

    def getSha(self):
        return self.sha

    def getPath(self):
        return self.path



def isValidHash(word):
    return len(word) == 64



def twoWordsFromLine(line):
    words = line.strip().split()
    if len(words) != 2:
        raise f'Line contains more than 2 words: "{line}"'
    return words



def readEntries(fileHandle):
    """Read entries from a file handle stream"""
    entries = []

    while True:
        line = fileHandle.readline()
        if not line:
            return entries

        words = twoWordsFromLine(line)
        if not isValidHash(words[0]):
            logging.error(f'found a weird line without hash: "{line}"')
            continue

        sha = words[0]
        path = words[1]
        newEntry = entry(sha, path)
        entries.append(newEntry)



def listToDict(listOfEntries):
    dic = {}
    for entry in listOfEntries:
        if entry.getSha() in dic:
            dic[entry.getSha()].append(entry.getPath())
        else:
            dic[entry.getSha()] = [entry.getPath()]
    return dic



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Incorrect usage, specify two files!")
        sys.exit(1)

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

# TODO: add a test for this function
# Find entries that are duplicate within old file and print them out
def findDupeHashes(dic):
    for sha in dic:
        if len(dic[sha]) > 1:
            for path in dic[sha]:
                print("+ " + path)
            print("")
