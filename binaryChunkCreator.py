import os.path
import sys
from os import path

fileName = input("Enter fileName you want to break into chunks: ")

if not path.exists(fileName):
    print ("File does not exist")
    sys.exit()

CHUNK_SIZE = int(input("Enter the chunk size: "))
file_number = 1

with open(fileName) as f:
    chunk = f.read(CHUNK_SIZE)
    while chunk:
        with open(fileName + str(file_number), 'w+') as chunk_file:
            chunk_file.write(chunk)
        file_number += 1
        chunk = f.read(CHUNK_SIZE)