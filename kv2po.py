#!/usr/bin/python3

import sys
import errno
import os
import re
import shutil
import datetime
import argparse
import kvutil

KV_PATTERN = re.compile("^[\s\t]*\"([^\"]*)\"[\s\t]*\"([^\"]*)\"")
COMMENT_PATTERN = re.compile("^[\s\t]*//")
LINE_EMPTY_PATTERN = re.compile("^[\s\t\n]*$")
ONLY_VALUE_PATTERN = re.compile("^[\s\t]*\"([^\"]*)\"[\s\t]*$")

VERSION = 1
BUG_ADDRESS = "https://github.com/AngelArenaAllstars/suggestions/issues"
LANGUAGE = "en"
HEADLINE = "Translation of Open Angel Arena"

HEADER_END = kvutil.HEADER_END

error_counter = 0

def printHeader(output):
    output.write("# {}\n".format(HEADLINE))
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
    
def convertStreamToStream(kvInputStream, poOutputStream, inputFileName, uniqueIds):
    global error_counter
    for i, line in enumerate(kvInputStream):            # Iterate over lines
        if COMMENT_PATTERN.match(line):   # Ignore Comment
            # poOutputStream.write( "# {}".format(line))
            pass
        elif LINE_EMPTY_PATTERN.match(line) or line == "":
            poOutputStream.write(line)
        else:
            kvPair = KV_PATTERN.match(line)
            if kvPair:              # kv-pair
                key = kvPair.group(1)
                value = kvPair.group(2)
                
                if key not in uniqueIds:
                    uniqueIds.add(key)
                    poOutputStream.write("#: {}\n".format(inputFileName))
                    poOutputStream.write("msgctxt \"{}\"\n".format(key))
                    poOutputStream.write("msgid \"{}\"\n".format(value))
                    poOutputStream.write("msgstr \"\"\n\n")
                else:
                    print ("[DUPLICATE] {0}[{1}]\n{2}".format(inputFileName, i, line))
                    error_counter += 1
            elif ONLY_VALUE_PATTERN.match(line):
                print ("[ONLY_KEY] {0}[{1}]\n{2}".format(inputFileName, i, line))
                error_counter += 1
            else:
                print ("[MATCH_ERROR] {0}[{1}]\n{2}".format(inputFileName, i, line))
                error_counter += 1         
                
argparser = argparse.ArgumentParser(description='Convert from kv-format to po-format.')
argparser.add_argument('source', metavar='SOURCE', type=str, help='if --one_file_in is set, then source file, otherwise source directory.')
argparser.add_argument('destination', metavar='DESTINATION', type=str, help='if --one_file_out is set, then destination file, otherwise destination directory.')
argparser.add_argument('-o', '--one_file_in', dest='oneFileIn', action='store_true', help='Should the files be processed from a single file? ')
argparser.add_argument('-O', '--one_file_out', dest='oneFileOut', action='store_true', help='Should the files be processed into a single file? ')
argparser.add_argument('-e', '--input_extensions', metavar='INPUT_EXTENSION', dest='inputExtensions', type=str, default=['.txt'], nargs='+', help='one or more file extensions for input file, for example \'.txt\'.')
argparser.add_argument('-E', '--output_extension', metavar='OUTPUT_EXTENSION', dest='outputExtension', type=str, default='.pot', help='file extension for output file, for example \'.pot\'.')

args = argparser.parse_args()

source = args.source
destination = args.destination
oneFileIn = args.oneFileIn
oneFileOut = args.oneFileOut
inputExtensions = args.inputExtensions
outputExtension = args.outputExtension

if oneFileIn:
    sourceFile = source
    if not os.path.isfile(sourceFile):
        raise Exception('The source-file {} doesn\'t exist!'.format(sourceFile))
    sourceDirectory = os.path.dirname(sourceFile)
    sourceFileBasename = os.path.basename(sourceFile)
else:
    def shouldFileBeProcessed( file ):
        return os.path.isfile(file) and os.path.splitext(file)[1] in inputExtensions
    sourceDirectory = source
    sourceFiles = list(\
    filter(lambda n: shouldFileBeProcessed( n ), \
        map(lambda bn: os.path.join(sourceDirectory, bn), os.listdir(sourceDirectory))))
    sourceFileBasenames = list(map(lambda n: os.path.basename(n), sourceFiles))

if oneFileOut:
    destinationFile = destination
    destinationDirectory = os.path.dirname(destinationFile)
    destinationBasename = os.path.basename(destinationFile)
else:
    if oneFileIn:
        raise Exception("Can't process from one file into multiple files!")
    destinationDirectory = destination
    destinationFileBasenames = list(map(lambda bn: os.path.splitext(bn)[0] + outputExtension, sourceFileBasenames))
    destinationFiles = list(map(lambda bn: os.path.join(destinationDirectory, bn), destinationFileBasenames))

ids = set([])

if not os.path.isdir(sourceDirectory):
    raise Exception('The source-directory {} doesn\'t exist!'.format(sourceDirectory))

    
#if os.path.exists(destination):
    #shutil.rmtree(destination)
os.makedirs(destinationDirectory, exist_ok=True)

if oneFileIn and oneFileOut:                    # file to file
    with open(destinationFile, 'w+') as destinationStream:
        printHeader(destinationStream)
        with open(sourceFile) as sourceStream:
            convertStreamToStream(sourceStream, destinationStream, sourceFileBasename, ids)
            # print("Wrote file {0} to {1}".format(fInput, fOutput))
elif not oneFileIn and oneFileOut:              # directory to file
    with open(destinationFile, 'w+') as destinationStream:
        printHeader(destinationStream)
        for sourceFile, sourceFileBasename in zip(sourceFiles, sourceFileBasenames):
            with open(sourceFile) as sourceStream:
                convertStreamToStream(sourceStream, destinationStream, sourceFileBasename, ids)
                # print("Wrote file {0} to {1}".format(fInput, fOutput))
elif not oneFileIn and not oneFileOut:          # directory to directory
    for (sourceFile, sourceFileBasename, destinationFile, destinationFileBasename) in \
        zip(sourceFiles, sourceFileBasenames, destinationFiles, destinationFileBasenames):
        with open(destinationFile, 'w+') as destinationStream:
            printHeader(destinationStream)
            with open(sourceFile) as sourceStream:
                convertStreamToStream(sourceStream, destinationStream, sourceFileBasename, ids)
else:
    # Not possible
    pass
print("Finished with {} errors!".format(error_counter))

