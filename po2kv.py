#!/usr/bin/python3

import sys
import errno
import os
import re
import shutil
import datetime
import kvutil
import argparse


NUM_OF_ARGUMENTS = 3
HEADER_END = kvutil.HEADER_END
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

def convertStreamToStream(kvInputStream, kvOutputStream):
    phase = SKIPPING_HEADER
    resetKeyValue()
    for i, line in enumerate(kvInputStream):                     # Iterate over lines
        if phase == SKIPPING_HEADER:
            if HEADER_END_PATTERN.match(line):
                phase = EXPECTING_FILE_NAME
        elif LINE_EMPTY_PATTERN.match(line):
            pass
        elif phase == EXPECTING_FILE_NAME:
            match = KV_FILE_NAME_PATTERN.match(line)
            if match:
                phase = EXPECTING_MSGCTXT
            else:
                skipLine(phase, sourceFile, i, line)
        elif phase == EXPECTING_MSGCTXT:
            match = MSGCTXT_PATTERN.match(line)
            if match:
                key = match.group(1)
                phase = EXPECTING_MSGID
            else:
                skipLine(phase, sourceFile, i, line)
        elif phase == EXPECTING_MSGID:
            match = MSGID_PATTERN.match(line)
            if match:
                phase = EXPECTING_MSGSTR
            else:
                skipLine(phase, sourceFile, i, line)
        elif phase == EXPECTING_MSGSTR:
            match = MSGSTR_PATTERN.match(line)
            if match:
                value = match.group(1)
                kvPair = "\"{0}\" \"{1}\"\n".format(key, value)
                kvOutputStream.write(kvPair)
                resetKeyValue()
                phase = EXPECTING_FILE_NAME
            else:
                skipLine(phase, sourceFile, i, line)
        else:
            print("Shouldn't happen.")
            skipLine(phase, sourceFile, i, line)

    
argparser = argparse.ArgumentParser(description='Convert from po-format to kv-format.')
argparser.add_argument('source', metavar='SOURCE', type=str, help='if --one_file_in is set, then source file, otherwise source directory.')
argparser.add_argument('destination', metavar='DESTINATION', type=str, help='if --one_file_out is set, then destination file, otherwise destination directory.')
argparser.add_argument('-o', '--one_file_in', dest='oneFileIn', action='store_true', help='Should the files be processed from a single file? ')
argparser.add_argument('-O', '--one_file_out', dest='oneFileOut', action='store_true', help='Should the files be processed into a single file? ')
argparser.add_argument('-e', '--input_extensions', metavar='INPUT_EXTENSION', dest='inputExtensions', type=str, default=['.po'], nargs='+', help='one or more file extensions for input file, for example \'.po\'.')
argparser.add_argument('-E', '--output_extension', metavar='OUTPUT_EXTENSION', dest='outputExtension', type=str, default='.txt', help='file extension for output file, for example \'.txt\'.')

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
    sourceBasename = os.path.basename(sourceFile)
else:
    def shouldFileBeProcessed( file ):
        return os.path.isfile(file) and os.path.splitext(file)[1] in inputExtensions
    sourceDirectory = source
    sourceFiles = list(\
    filter(lambda n: shouldFileBeProcessed( n ), \
        map(lambda bn: os.path.join(sourceDirectory, bn), os.listdir(sourceDirectory))))
    sourceFileBasenames = list(map(lambda n: os.path.basename(n), sourceFiles))

if oneFileOut:
    if not oneFileIn:
        raise Exception("Can't process from multiple files into one file!")
    destinationFile = destination
    destinationDirectory = os.path.dirname(destinationFile)
    destinationBasename = os.path.basename(destinationFile)
else:
    destinationDirectory = destination
    if not oneFileIn:
        destinationFileBasenames = list(map(lambda bn: os.path.splitext(bn)[0] + outputExtension, sourceFileBasenames))
        destinationFiles = list(map(lambda bn: os.path.join(destinationDirectory, bn), destinationFileBasenames))


SKIPPING_HEADER = 0
EXPECTING_FILE_NAME = 1
EXPECTING_MSGCTXT = 2
EXPECTING_MSGID = 3
EXPECTING_MSGSTR = 4
    
#if os.path.exists(destination):
    #shutil.rmtree(destination)
os.makedirs(destinationDirectory, exist_ok=True)

if oneFileIn and oneFileOut:
    with open(destinationFile, 'w+') as destinationStream:
        with open(sourceFile) as sourceStream:
            convertStreamToStream(sourceStream, destinationStream)
if oneFileIn and not oneFileOut:
    with open(sourceFile) as sourceStream:
        phase = SKIPPING_HEADER
        destinationFileBasename = ""
        resetKeyValue()
        destinationStream = None
        for i, line in enumerate(sourceStream):                     # Iterate over lines
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
                    skipLine(phase, sourceFile, i, line)
            elif phase == EXPECTING_MSGCTXT:
                match = MSGCTXT_PATTERN.match(line)
                if match:
                    key = match.group(1)
                    phase = EXPECTING_MSGID
                else:
                    skipLine(phase, sourceFile, i, line)
            elif phase == EXPECTING_MSGID:
                match = MSGID_PATTERN.match(line)
                if match:
                    phase = EXPECTING_MSGSTR
                else:
                    skipLine(phase, sourceFile, i, line)
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
                    skipLine(phase, sourceFile, i, line)
            else:
                print("Shouldn't happen.")
                skipLine(phase, sourceFile, i, line)
        if destinationStream:
            destinationStream.close()

if not oneFileIn and not oneFileOut:
    for (sourceFile, destinationFile) in zip(sourceFiles, destinationFiles):
        with open(destinationFile, 'w+') as destinationStream:
            with open(sourceFile) as sourceStream:
                convertStreamToStream(sourceStream, destinationStream)
