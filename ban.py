# ban - backup analyzer
# Given two files with a format
#   <checksum> <file path>
# Will output:
#  1. Checksums and their file paths that are present in the first file but not in the second one
#  2. Bash commands to copy the changed files to a different location

# Glossary
# Snapshot - a copy of data. When you copy your data to a backup device, the resulting files are called a snapshot.
# Snapshot hashfile - a file generated by running sha256sum on every file in a snapshot.
#   Contains a hash and a filepath in every line.
# Snapshot entry - a representation of a file from a snapshot.
#   The snapshot entry has a hash and a path inside of the snapshot.
# Snapshot diff - a list of snapshot entries that exist in one snapshot,
#   but are missing in another one.
# Missing snapshot entry - means that the file that existed at a path and had a hash now either:
#   - has the same hash but a different path (was moved)
#   - has the same path but a different hash (was modified)
# Hash index - a dictionary representation, where key is the hash and values are the paths


import sys
import os
import logging
import argparse



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
    twoSpacePosition = line.find('  ')
    if twoSpacePosition != -1:
        # +2 because we want first char after two spaces
        return line[:twoSpacePosition], line[twoSpacePosition+2:]

    logging.error(f'Input line does not contain a normal two-space separator: "{line}"')

    spacePosition = line.find(' ')
    if spacePosition != -1:
        # +1 because we want the first char after the space
        return line[:spacePosition], line[spacePosition+1:]

    logging.error(f'Input line also does not contain a single-space separator: "{line}"')
    return None, None



def readEntries(fileHandle):
    """Read entries from a file handle stream"""
    entries = []

    while True:
        line = fileHandle.readline()
        if not line:
            return entries

        fileHash, filePath = parseHashAndPath(line)
        if not fileHash or not filePath:
            logging.error('continuing to next line...')
            continue

        if not isValidHash(fileHash):
            logging.error(f'found a weird line without hash: "{line}"')
            continue

        # The -1 and the very end removes the new line \n character introduced by the readline() method
        if filePath[-1] == '\n':
            newEntry = Entry(fileHash, filePath[:-1])
        else:
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



def getOldEntriesMissingFromNew(old, new):
    missing = []
    for sha in old:
        if not sha in new:
            for path in old[sha]:
                missing.append(Entry(sha, path))
    return missing



def keepPath(path, pathsToSkip):
    for p in pathsToSkip:
        logging.error(f'"{path}" startswith "{p}"')
        if path.startswith(p):
            return False
    return True



def filterEntries(entries, pathsToSkip):
    return [x for x in entries if keepPath(x.getPath(), pathsToSkip)]



def bashPrintMissingEntry(entry, targetPath):
    '''Print a ready for execution bash command to copy a missing file'''

    fileName = os.path.basename(entry.getPath())
    targetFolder = os.path.join(targetPath, os.path.dirname(entry.getPath()))
    targetFile = os.path.join(targetFolder, fileName)

    return f'mkdir -p {targetFolder} && cp -a {entry.getPath()} {targetFile}'



def get_parsed_arguments():
    parser = argparse.ArgumentParser(prog='Snapshot hashfile analyzer',
                                     description='Compares the two hashfiles of snapshots, prints missing entries',
                                     epilog='by Oleg Krasnianskyi')

    parser.add_argument('-e', '--early-hashes',
                        type=argparse.FileType('r'),
                        required=True,
                        help='hash file for the first snapshot')

    parser.add_argument('-l', '--late-hashes',
                        type=argparse.FileType('r'),
                        required=True,
                        help='hash file for the late snapshot')

    parser.add_argument('-s', '--skip',
                        help='paths from early snapshot to ingnore when comparing with late snapshot')

    return parser.parse_args()



if __name__ == '__main__':
    args = get_parsed_arguments()

    early_entries = []
    late_entries = []

    try:
        early_entries= readEntries(args.early_hashes)
    except SpaceNotFound as e:
        raise RuntimeError(f'Early hashes file has a bad line: {str(e)}')

    try:
        late_entries = readEntries(args.late_hashes)
    except SpaceNotFound as e:
        raise RuntimeError(f'Late hashes file has a bad line: {str(e)}')

    print(f'Number of early entries: {len(early_entries)}')
    print(f'Number of late entries: {len(late_entries)}')

    # Create a dictionary of entries
    early_hash_map = listToDict(early_entries)
    late_hash_map = listToDict(late_entries)

    # Find entries that are present in the old dictionary, but are missing in the second one:
    oldEntriesMissingFromNew = getOldEntriesMissingFromNew(early_hash_map, late_hash_map)

    pathsToSkip = ['./seagate-backup-2021-05-03/SteamLibrary']#/steamapps/common/Counter-Strike Global Offensive/']
    missingEntriesFiltered = filterEntries(oldEntriesMissingFromNew, pathsToSkip)

    for e in missingEntriesFiltered: print(bashPrintMissingEntry(e, '/node/save/'))



# Find entries that are duplicate within old file and print them out
def findDupeHashes(dic):
    for sha in dic:
        if len(dic[sha]) > 1:
            for path in dic[sha]:
                print("+ " + path)
            print("")
