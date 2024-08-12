# ban - backup analyzer
# Given two files with a format
#   <checksum> <file path>
# Will output:
#  1. Checksums and their file paths that are present in the first file but not in the second one

import sys
import logging



class SpaceNotFound(Exception):
    pass



class Entry:
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



def parseHashAndPath(line):
    spacePosition = line.find(' ')
    if spacePosition == -1:
        raise SpaceNotFound(f'Input line does not contain a space: "{line}"')
    return line[:spacePosition], line[spacePosition+1:]



def readEntries(fileHandle):
    """Read entries from a file handle stream"""
    entries = []

    while True:
        line = fileHandle.readline()
        if not line:
            return entries

        fileHash, filePath = parseHashAndPath(line)
        if not isValidHash(fileHash):
            logging.error(f'found a weird line without hash: "{line}"')
            continue

        newEntry = Entry(fileHash, filePath)
        entries.append(newEntry)



def listToDict(listOfEntries):
    """Returns a dictionary with has as a key and the value beiing a list of paths
    sharing the same hash"""

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
        try:
            oldEntries = readEntries(ob)
        except SpaceNotFound as e:
            raise RuntimeError(f'Input file {oldBackup} has a bad line: {str(e)}')

    with open(newBackup) as nb:
        try:
            newEntries = readEntries(nb)
        except SpaceNotFound as e:
            raise RuntimeError(f'Input file {newBackup} has a bad line: {str(e)}')

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
