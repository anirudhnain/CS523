import boto3
import random
import string
import os.path
import sys
import time
from os import path

def upload_file(file_name, bucket, s3, content):
    print(file_name)
    PREFIX = 'testing/'
    s3.Object(bucket, PREFIX+file_name).put(Body=content)

# def createChunksForFileAndUploadToS3(fileName, bucket, s3, CHUNK_SIZE):
    
#     if not path.exists(fileName):
#         print ("File does not exist")
#         sys.exit()

#     file_number = 1
#     chunksNames = []

#     with open(fileName) as f:
#         chunk = f.read(CHUNK_SIZE)
#         while chunk:
#             extension = fileName.split(".")[-1]
#             chunkName = fileName.split(".")[0] + str(file_number) + "."+extension
#             with open(chunkName, 'w+') as chunk_file:
#                 chunk_file.write(chunk)
#             chunksNames.append(chunkName)
#             upload_file(chunkName, bucket, s3, open(chunkName, "r").read())
#             file_number += 1
#             chunk = f.read(CHUNK_SIZE)
#     return chunksNames


KEY_ID = ""
ACCESS_KEY = ""
bucket = "speedfs"

s3 = boto3.resource(
    's3',
    aws_access_key_id=KEY_ID,
    aws_secret_access_key=ACCESS_KEY
)

# #Enter the file name you want to read from the system
# fileName = input("Enter fileName you want to write to S3: ")

# chunksNames = createChunksForFileAndUploadToS3(fileName, bucket, s3, 8000000)

start_time = time.time()

# write to last chunk
with open("test.txt", 'a') as chunk_file:
    chunk_file.write("  *******append new data**********")

# print (open("test131.txt", "r").read())
upload_file("test.txt", bucket, s3, open("test.txt", "r").read())


print("--- %s seconds ---" % (time.time() - start_time))