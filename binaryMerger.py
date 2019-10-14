import os.path
from os import path

fileName = input("Enter fileName you want to merge chunks for without specifying the chunck number: ")
fileNumber = 1

newFile = open(fileName,'w+')


while True:
    chunkFileName = fileName + str(fileNumber)
    if path.exists(chunkFileName):
        with open(chunkFileName) as f:
            chunk = f.read()
            with open(fileName, 'a') as merge_file:
                merge_file.write(chunk)
            fileNumber+=1
        os.remove(chunkFileName)
    else:
        break