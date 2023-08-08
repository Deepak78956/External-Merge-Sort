import random
import string
import operator
import pprint as p
import math


def countRecords(lst):
    count = 0
    subsequentFiles = []
    for i in range(len(lst)):
        for j in range(len(lst[i])):
            if(lst[i][j] == "NULL"):
                continue
            if(".txt" in lst[i][j]):
                subsequentFiles.append(lst[i][j])
                continue
            count += 1
    while(len(subsequentFiles)):
        file = subsequentFiles[0]
        with open(f"sorted_runs/{file}") as f:
            for line in f:
                if(".txt" in line):
                    subsequentFiles.append(line)
                    continue
                if("NULL" in line):
                    continue
                count += 1
        subsequentFiles.remove(file)
    return count


def mergeRLessThanM(lst, mergeFileName, B):
    noRec = countRecords(lst)
    extraRecords = noRec % B
    noBlocks = noRec // B
    k = 0
    heap = []
    for i in range(len(lst)):
        heap.append(lst[i][0])
    block = []
    while(len(lst)):
        minimum = min(heap, key=operator.itemgetter(1))
        block.append(minimum)
        if(len(block) == B):
            if(k == 0):
                with open(f"sorted_runs/{mergeFileName}.txt", 'w') as f:
                    for m in block:
                        transID, transAmt, cusName, cat = m
                        string = ' '.join(
                            [str(transID), str(transAmt), cusName, str(cat)])
                        f.write(string + "\n")
                    if(noBlocks == 1 and extraRecords == 0):
                        f.write("NULL")
                    else:
                        f.write(f"{mergeFileName}_subFile{k + 1}.txt")
                    noBlocks -= 1
                k += 1
            else:
                with open(f"sorted_runs/{mergeFileName}_subFile{k}.txt", 'w') as f:
                    for m in block:
                        transID, transAmt, cusName, cat = m
                        string = ' '.join(
                            [str(transID), str(transAmt), cusName, str(cat)])
                        f.write(string + "\n")
                    if(noBlocks == 1 and extraRecords == 0):
                        f.write("NULL")
                    else:
                        f.write(f"{mergeFileName}_subFile{k + 1}.txt")
                    noBlocks -= 1
                k += 1
            block = []
        extractedMinRunNo = heap.index(minimum)
        indexOfEle = lst[extractedMinRunNo].index(minimum)
        nextEle = lst[extractedMinRunNo][indexOfEle + 1]
        if(".txt" in nextEle):
            nextFile = nextEle
            buffer = []
            with open(f"sorted_runs/{nextFile}", 'r') as f:
                for line in f:
                    if(".txt" in line or "NULL" in line):
                        buffer.append(line)
                    else:
                        transID, transAmt, cusName, cat = line.strip().split(' ')
                        buffer.append([transID, int(transAmt), cusName, cat])
            lst[extractedMinRunNo] = buffer
            nextEle = buffer[0]

        elif("NULL" in nextEle):
            lst.pop(extractedMinRunNo)
            heap.remove(minimum)
            continue

        heap[extractedMinRunNo] = nextEle
    if(extraRecords):
        with open(f"sorted_runs/{mergeFileName}_subFile{k}.txt", 'w') as f:
            for m in block:
                transID, transAmt, cusName, cat = m
                string = ' '.join(
                    [str(transID), str(transAmt), cusName, str(cat)])
                f.write(string + "\n")
            f.write("NULL")


def mergeRuns(numberOfRecords, entryPoints, B, M):
    if(B > numberOfRecords):
        return "1.txt"
    i = 0
    while(len(entryPoints) >= M):
        mergeFileName = f"merge_file_{i}"
        lst = []
        for j in range(M):
            file = entryPoints[0]
            with open(f"sorted_runs/{file}", 'r') as f:
                lstFile = []
                for line in f:
                    if(".txt" in line or "NULL" in line):
                        lstFile.append(line)
                    else:
                        transID, transAmt, cusName, cat = line.strip().split(' ')
                        lstFile.append([transID, int(transAmt), cusName, cat])
                lst.append(lstFile)
            entryPoints.remove(entryPoints[0])
        mergeRLessThanM(lst, mergeFileName, B)
        entryPoints.append(f"{mergeFileName}.txt")
        i += 1
    mergeFileName = f"merge_file_{i}"
    lst = []
    for j in range(len(entryPoints)):
        file = entryPoints[0]
        with open(f"sorted_runs/{file}", 'r') as f:
            lstFile = []
            for line in f:
                if(".txt" in line or "NULL" in line):
                    lstFile.append(line)
                else:
                    transID, transAmt, cusName, cat = line.strip().split(' ')
                    lstFile.append([transID, int(transAmt), cusName, cat])
            lst.append(lstFile)
        entryPoints.remove(entryPoints[0])
    mergeRLessThanM(lst, mergeFileName, B)
    return mergeFileName


def createRuns(M, numberOfBlocks, B):
    entryPoints = []
    extraBlocks = numberOfBlocks % M
    numberOfRuns = math.ceil(numberOfBlocks / M)
    counter = 1
    cntr = 1
    nextFile = "1.txt"
    for i in range(numberOfRuns):
        if(extraBlocks and i == numberOfRuns - 1):
            M = extraBlocks
        lst = []
        for j in range(M):
            with open(f"blocks/{nextFile}", 'r') as f:
                for line in f:
                    if(line != 'NULL'):
                        if(".txt" in line):
                            nextFile = line
                            continue
                        transID, transAmt, cusName, cat = line.strip().split(' ')
                        lst.append(
                            [int(transID), int(transAmt), cusName, int(cat)])
            counter += 1
        lst.sort(key=operator.itemgetter(1))
        recordsLeft = len(lst)
        for k in range(M):
            with open(f"sorted_runs/{cntr}.txt", 'w') as f:
                for l in range(min(B, recordsLeft)):
                    transID, transAmt, cusName, cat = lst[B * k + l]
                    string = ' '.join(
                        [str(transID), str(transAmt), cusName, str(cat)])
                    f.write(string + "\n")
                cntr += 1
                if(k == M - 1):
                    entryPoints.append(f"{cntr - k - 1}.txt")
                    f.write("NULL")
                else:
                    f.write(f"{cntr}.txt")
            recordsLeft -= B
    return entryPoints


def createBlocks(B, numberOfRecords):
    with open("main.txt", 'r') as f:
        extraRecords = numberOfRecords % B
        numberOfBlocks = numberOfRecords // B
        r = numberOfBlocks if extraRecords else numberOfBlocks - 1
        for i in range(r):
            with open(f"blocks/{i + 1}.txt", 'w') as b:
                for j in range(B):
                    b.write(f.readline())
                b.write(f"{i + 2}.txt")

        if(extraRecords):
            with open(f"blocks/{numberOfBlocks + 1}.txt", 'w') as b:
                for i in range(extraRecords):
                    b.write(f.readline())
                b.write("NULL")
            return numberOfBlocks + 1
        with open(f"blocks/{numberOfBlocks}.txt", 'w') as b:
            for i in range(B):
                b.write(f.readline())
            b.write("NULL")
        return numberOfBlocks


def createMainRecordFile(numberOfRecords):
    with open("main.txt", 'w') as f:
        for i in range(numberOfRecords):
            salesAmount = random.randint(1, 60000)
            customerName = ''.join(random.choice(string.ascii_lowercase)
                                   for i in range(3))
            category = random.randint(1, 1500)
            f.write(f"{i + 1} {salesAmount} {customerName} {category}\n")


# <------------------------------------------ MAIN ------------------------------------------->
# Change the values here and kindly delete the files in sorted_runs and blocks folder before checking the output
# I am printing the final output file name using which subsequent blocks can be checked for correct output
# eg. finalFile = <something.txt> , using this final file subsequent files can be acquired as this file has linked file name at the end of file and so on
B = 500
M = 10
numberOfRecords = 50000
# <---- DRIVER CODE ---->
createMainRecordFile(numberOfRecords)
numberOfBlocks = createBlocks(B, numberOfRecords)
entryPoints = createRuns(M, numberOfBlocks, B)
finalFile = mergeRuns(numberOfRecords, entryPoints, B,
                      M - 1)  # previously here M is there
# <--------------------->
print(finalFile)  # Name of the final file having linked files for sorted sequence
# <---- Code to make final sorted sequence with all linked file in a single file ---->
exitLoop = 1
counter = 0
finalOutputLst = []
while(exitLoop):
    if(".txt" not in finalFile):
        finalFile = finalFile + ".txt"
    with open(f"sorted_runs/{finalFile}") as f:
        for line in f:
            if(line == "NULL"):
                exitLoop = 0
                break
            if(".txt" in line):
                finalFile = line
                break
            finalOutputLst.append(line)
            counter += 1
with open("final_output_file.txt", 'w') as f:
    for i in finalOutputLst:
        f.write(i)
# <------------------------------------------------------------------------------------------------>
