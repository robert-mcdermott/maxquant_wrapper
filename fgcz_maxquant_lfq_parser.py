#!/usr/local/bin/python3
# Simon Barkow-Oesterreicher
# 20140218


def parseHeaderLFQintensity(lines):
    #print("parseHeaderLFQintensity called")
    # get indexes for Intensity columns
    i = 0
    j = 0
    localIntensityIndexLFQ = 0
    for h in lines[0]:
        if h.startswith('LFQ intensity'):
            #print("intensity found")
            #print(h)
            if j == 0:
                localIntensityIndexLFQ = i
            #print("debug first index: ")
            #print(localIntensityIndexLFQ)
            localLastIntensityForFileIndexLFQ = i
            j += 1
        i += 1
    
    return localIntensityIndexLFQ, localLastIntensityForFileIndexLFQ

def parseHeaderMSMScounts(lines):
    #print("parseHeaderLFQintensity called")
    # get indexes for Intensity columns
    i = 0
    j = 0
    localMSMSIndexLFQ = 0
    for h in lines[0]:
        if h.startswith('MS/MS Count'):
            #print("intensity found")
            #print(h)
            if j == 0:
                localMSMSIndexLFQ = i
            #print("debug first index: ")
            #print(localIntensityIndexLFQ)
            localLastMSMSForFileIndexLFQ = i
            j += 1
        i += 1
    
    return localMSMSIndexLFQ, localLastMSMSForFileIndexLFQ


def parseHeaderIntensity(lines):
    # get indexes for Intensity coulumns
    i = 0
    intensityIndex = 0
    for h in lines[0]:
        if h == 'Intensity':
            intensityIndex = i
        if h.startswith('Intensity '):
            lastIntensityForFileIndex = i
        i += 1
    
    return intensityIndex, lastIntensityForFileIndex

def filterForLFQintensityQuantValues(inputFileLines, outputFilePath):
    intensityIndex, lastIntensityForFileIndex = parseHeaderLFQintensity(inputFileLines)
    numberOfFiles = lastIntensityForFileIndex - intensityIndex
    outFile = open(outputFilePath, "w")
    for l in inputFileLines:
        print(l[1], file = outFile, end='\t')
        for item in l[(lastIntensityForFileIndex)-numberOfFiles:lastIntensityForFileIndex]:
            print(item, file = outFile,  end='\t')
        for item in l[lastIntensityForFileIndex:lastIntensityForFileIndex+1]:
            print(item, file = outFile,  end='\n')

def filterForMSMScountValues(inputFileLines, outputFilePath):
    MSMScountIndex, lastMSMScountForFileIndex = parseHeaderMSMScounts(inputFileLines)
    numberOfFiles = lastMSMScountForFileIndex - MSMScountIndex
    outFile = open(outputFilePath, "w")
    for l in inputFileLines:
        print(l[1], file = outFile, end='\t')
        for item in l[(lastMSMScountForFileIndex)-numberOfFiles:lastMSMScountForFileIndex]:
            print(item, file = outFile,  end='\t')
        for item in l[lastMSMScountForFileIndex:lastMSMScountForFileIndex+1]:
            print(item, file = outFile,  end='\n')



def filterForIntensityQuantValues(inputFileLines, outputFilePath):
    intensityIndex, lastIntensityForFileIndex = parseHeaderIntensity(inputFileLines)
    numberOfFiles = lastIntensityForFileIndex - intensityIndex
    outFile = open(outputFilePath, "w")
    for l in inputFileLines:
        print(l[1], file = outFile, end='\t')
        for item in l[(lastIntensityForFileIndex+1)-numberOfFiles:lastIntensityForFileIndex]:
            print(item, file = outFile,  end='\t')
        for item in l[lastIntensityForFileIndex:lastIntensityForFileIndex+1]:
            print(item, file = outFile,  end='\n')


def checkFile(inputFileLines):
    numberOfColumns=len(inputFileLines[0])
    for line in inputFileLines:
        if len(line) != numberOfColumns:
            return False
    return True

def removeColumnByHeaderName(inputFileLines, outputFilePath, columnName):
    header = inputFileLines[0]
    indexOfFastaDesctiptionColumn= header.index(columnName)
    outFile = open(outputFilePath, "w")
    print('\t'.join(header),file = outFile, end='')
    for l in inputFileLines[1:]:
        print('\t'.join(l[:indexOfFastaDesctiptionColumn]+[""]+l[indexOfFastaDesctiptionColumn+1:]), file = outFile, end='')

import sys, getopt

def main(argv):
    inputFilePath = ''
    outputFilePath = ''
    function = ''
    if len(argv) != 6:
        print('MaxQuant_LFQ_parser.py -i <inputFilePath> -o <outputFilePath> -u <removeColumn|filterIntensity|filterLFQintensity|filterMSMScounts>')
        sys.exit()
    try:
        opts,arg = getopt.getopt(argv,"hi:o:u:",["ifile=","ofile=","function="])
    except getopt.GetoptError:
        print('MaxQuant_LFQ_parser.py -i <inputFilePath> -o <outputFilePath> -u <removeColumn|filterIntensity|filterLFQintensity|filterMSMScounts>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputFilePath> -o <outputFilePath>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputFilePath = arg
        elif opt in ("-o", "--ofile"):
            outputFilePath = arg
        elif opt in ("-u", "--function"):
            function = arg
    
    inputFile = open(inputFilePath)
    inputFileLines=[]
    for line in inputFile:
        inputFileLines.append(line.split('\t'))
    
    if checkFile(inputFileLines):
        pass
    else:
        print("The input file seems to be corrupt")
        sys.exit()
    
    if function == 'filterIntensity':
        filterForIntensityQuantValues(inputFileLines, outputFilePath)
    elif function == 'filterLFQintensity':
        filterForLFQintensityQuantValues(inputFileLines, outputFilePath)
    elif function == 'filterMSMScounts':
        filterForMSMScountValues(inputFileLines, outputFilePath)
    elif function == 'removeColumn':
        removeColumnByHeaderName(inputFileLines, outputFilePath, 'Fasta headers')
    else:
        print("no function given. Exit.")
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])


