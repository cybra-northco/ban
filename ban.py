# ban - backup analyzer
# Given two files with a format
#   <checksum> <file path>
# Will output:
#  1. Checksums and their file paths that are present in the first file but not in the second one

# Glossary
# Snapshot - a copy of data. When you copy your data to a backup device, the resulting files are called a snapshot.
# Snapshot entry - a representation of a file from a snapshot.
#   The snapshot entry has a hash and a path inside of the snapshot.
# Snapshot diff - a list of snapshot entries that exist in one snapshot,
#   but are missing in another one.
# Missing snapshot entry - means that the file that existed at a path and had a hash now either:
#   - has the same hash but a different path (was moved)
#   - has the same path but a different hash (was modified)

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

    def __repr__(self):
        return f'{self.sha} {self.path}'



def isValidHash(word):
    return len(word) == 64



def parseHashAndPath(line):
    spacePosition = line.find(' ')
    if spacePosition == -1:
        logging.error(f'Input line does not contain a space: "{line}"')
        #raise SpaceNotFound(f'Input line does not contain a space: "{line}"')
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

        # The -1 and the very end removes the new line \n character introduced by the readline() method
        newEntry = Entry(fileHash, filePath[:-1])
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

def getOldEntriesMissingFromNew(old, new):
    missing = []
    for sha in old:
        if not sha in new:
            missing.append(Entry(sha, old[sha]))
    return missing



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
    oldEntriesMissingFromNew = getOldEntriesMissingFromNew(oldHashMap, newHashMap)
    for e in oldEntriesMissingFromNew: print(e)



# Find entries that are duplicate within old file and print them out
def findDupeHashes(dic):
    for sha in dic:
        if len(dic[sha]) > 1:
            for path in dic[sha]:
                print("+ " + path)
            print("")
