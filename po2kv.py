#!/usr/bin/python3

import sys
import errno
import os
import re
import shutil
import datetime

NUM_OF_ARGUMENTS = 3
HEADER_END = "################### HEADER END ###################"
HEADER_END_PATTERN = re.compile("{}".format(HEADER_END))

PATTERN_TEMPLATE = "^[\s\t]*{}[\s\t]*\"([^\"]*)\""
MSGCTXT_PATTERN = re.compile(PATTERN_TEMPLATE.format("msgctxt"))
MSGID_PATTERN = re.compile(PATTERN_TEMPLATE.format("msgid"))
MSGSTR_PATTERN = re.compile(PATTERN_TEMPLATE.format("msgstr"))
#KV_COMMENT_PATTERN = re.compile("^#([\s\t]*//.*)$")
KV_FILE_NAME_PATTERN = re.compile("^#:[\s\t]*([^:\n]*)")
LINE_EMPTY_PATTERN = re.compile("^[\s\t\n]*$")

def printPhase(phase):
    if phase == 0:
        return "SKIPPING_HEADER"
    elif phase == 1:
        return "EXPECTING_FILE_NAME"
    elif phase == 2:
        return "EXPECTING_MSGCTXT"
    elif phase == 3:
        return "EXPECTING_MSGID"
    elif phase == 4:
        return "EXPECTING_MSGSTR"

def skipLine(phase, sourceFile, counter, line):
    print("[SKIPPED_LINE] {0}[{1}]\nphase={2}\n{3}".format(sourceFile, counter, printPhase(phase), line))

def resetKeyValue():
    key = ""
    value = ""


if len(sys.argv) < NUM_OF_ARGUMENTS:
    raise Exception('The number of arguments has to be {}!'.format(NUM_OF_ARGUMENTS))

sourceFile = sys.argv[1]
destinationDirectory = sys.argv[2]


if not os.path.isfile(sourceFile):
    raise Exception('The source-file {} doesn\'t exist!'.format(sourceFile))

SKIPPING_HEADER = 0
EXPECTING_FILE_NAME = 1
EXPECTING_MSGCTXT = 2
EXPECTING_MSGID = 3
EXPECTING_MSGSTR = 4
    
#if os.path.exists(destination):
    #shutil.rmtree(destination)
os.makedirs(destinationDirectory, exist_ok=True)

if os.path.isfile(sourceFile):
    with open(sourceFile) as sourceStream:
        counter = 1
        phase = SKIPPING_HEADER
        destinationFileBasename = ""
        resetKeyValue()
        destinationStream = None
        for line in sourceStream:                     # Iterate over lines
            if phase == SKIPPING_HEADER:
                if HEADER_END_PATTERN.match(line):
                    phase = EXPECTING_FILE_NAME
            elif LINE_EMPTY_PATTERN.match(line):
                pass
            elif phase == EXPECTING_FILE_NAME:
                match = KV_FILE_NAME_PATTERN.match(line)
                if match:
                    phase = EXPECTING_MSGCTXT
                    newDestinationFileBasename = match.group(1)
                    if newDestinationFileBasename != destinationFileBasename:           # Change Destination-File if necessary
                        if destinationStream:
                            destinationStream.close()
                        destinationFileBasename = newDestinationFileBasename
                        destinationFile = os.path.join(destinationDirectory, destinationFileBasename)
                        destinationStream = open(destinationFile, 'w+')
                else:
                    skipLine(phase, sourceFile, counter, line)
            elif phase == EXPECTING_MSGCTXT:
                match = MSGCTXT_PATTERN.match(line)
                if match:
                    key = match.group(1)
                    phase = EXPECTING_MSGID
                else:
                    skipLine(phase, sourceFile, counter, line)
            elif phase == EXPECTING_MSGID:
                match = MSGID_PATTERN.match(line)
                if match:
                    phase = EXPECTING_MSGSTR
                else:
                    skipLine(phase, sourceFile, counter, line)
            elif phase == EXPECTING_MSGSTR:
                match = MSGSTR_PATTERN.match(line)
                if match:
                    value = match.group(1)
                    kvPair = "\"{0}\" \"{1}\"\n".format(key, value)
                    destinationStream.write(kvPair)
                    resetKeyValue()
                    phase = EXPECTING_FILE_NAME
                    #print("{0} -> {1}".format(kvPair, destinationFileBasename))
                else:
                    skipLine(phase, sourceFile, counter, line)
            else:
                print("Shouldn't happen.")
                skipLine(phase, sourceFile, counter, line)
            counter += 1
        if destinationStream:
            destinationStream.close()
