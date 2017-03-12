#!/usr/bin/python3

import sys
import errno
import os
import re
import shutil
import datetime

NUM_OF_ARGUMENTS = 3
INPUT_EXTENSIONS = [".txt"]
#OUTPUT_EXTENSION = ".pot"
#FILE_sourceFileBasename = "templates"
KV_PATTERN = re.compile("^[\s\t]*\"([^\"]*)\"[\s\t]*\"([^\"]*)\"")
COMMENT_PATTERN = re.compile("^[\s\t]*//")
LINE_EMPTY_PATTERN = re.compile("^[\s\t\n]*$")
ONLY_VALUE_PATTERN = re.compile("^[\s\t]*\"([^\"]*)\"[\s\t]*$")

VERSION = 1
BUG_ADDRESS = "https://github.com/AngelArenaAllstars/suggestions/issues"
LANGUAGE = "en"
HEADER_END = "################### HEADER END ###################"

def printHeader(output):
    output.write("# Translation of Open Angel Arena\n")
    output.write("#, fuzzy\n")
    output.write("msgid \"\"\n")
    output.write("msgstr \"\"\n")
    output.write("\"Project-Id-Version: {}\\n\"\n".format(VERSION))
    output.write("\"Report-Msgid-Bugs-To: {}\\n\"\n".format(BUG_ADDRESS))
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M+0100")
    output.write("\"POT-Creation-Date: {}\\n\"\n".format(timestamp))
    output.write("\"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n\"\n")
    output.write("\"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n\"\n")
    output.write("\"Language-Team: LANGUAGE <LL@li.org>\\n\"\n")
    output.write("\"Language: {}\\n\"\n".format(LANGUAGE))
    output.write("\"MIME-Version: 1.0\\n\"\n")
    output.write("\"Content-Type: text/plain; charset=UTF-8\\n\"\n")
    output.write("\"Content-Transfer-Encoding: 8bit\\n\"\n")
    output.write("{}\n\n".format(HEADER_END))

if len(sys.argv) < NUM_OF_ARGUMENTS:
    raise Exception('The number of arguments has to be {}!'.format(NUM_OF_ARGUMENTS))

sourceDirectory = sys.argv[1]
destinationFile = sys.argv[2]
destinationDirectory = os.path.dirname(destinationFile)

ids = set([])

if not os.path.isdir(sourceDirectory):
    raise Exception('The source-directory {} doesn\'t exist!'.format(sourceDirectory))

    
#if os.path.exists(destination):
    #shutil.rmtree(destination)
os.makedirs(destinationDirectory, exist_ok=True)

destinationStream = open(destinationFile, 'w+')
printHeader(destinationStream)
for sourceFileBasename in os.listdir(sourceDirectory):
    sourceFile = os.path.join(sourceDirectory, sourceFileBasename)
    if os.path.isfile(sourceFile): # Iterate over each file
        sourceFileBasenameSplit = os.path.splitext(sourceFileBasename)
        if sourceFileBasenameSplit[1] in INPUT_EXTENSIONS:  # Only go further, if the extension is in INPUT_EXTENSIONS
            with open(sourceFile) as sourceStream:
                counter = 1
                for line in sourceStream:                     # Iterate over lines
                    if COMMENT_PATTERN.match(line):   # Ignore Comment
                        # destinationStream.write( "# {}".format(line))
                           pass
                    elif LINE_EMPTY_PATTERN.match(line) or line == "":
                        destinationStream.write(line)
                    else:
                        kvPair = KV_PATTERN.match(line)
                        if kvPair:              # kv-pair
                            key = kvPair.group(1)
                            value = kvPair.group(2)
                            
                            if key not in ids:
                                ids.add(key)
                                destinationStream.write("#: {}\n".format(sourceFileBasename))
                                destinationStream.write("msgctxt \"{}\"\n".format(key))
                                destinationStream.write("msgid \"{}\"\n".format(value))
                                destinationStream.write("msgstr \"\"\n\n")
                            else:
                                print ("[DUPLICATE] {0}[{1}]\n{2}".format(sourceFileBasename, counter, line))
                        elif ONLY_VALUE_PATTERN.match(line):
                            print ("[ONLY_VALUE] {0}[{1}]\n{2}".format(sourceFileBasename, counter, line))
                        else:
                            print ("[MATCH_ERROR] {0}[{1}]\n{2}".format(sourceFileBasename, counter, line))
                    counter += 1
            # print("Wrote file {0} to {1}".format(fInput, fOutput))
destinationStream.close()
