import os.path
from os import path

import boto3

import time

def readFromS3(s3, key):
    bucket = "speedfs"
    obj = s3.Object(bucket, key)
    # print(obj.get()['Body'].read().decode('utf-8'))

# fileName = "test.txt"
# fileNumber = 1

# newFile = open(fileName,'w+')

start_time = time.time()

KEY_ID = ""
ACCESS_KEY = ""

s3 = boto3.resource(
    's3',
    aws_access_key_id=KEY_ID,
    aws_secret_access_key=ACCESS_KEY
)

readFromS3(s3, "testing/test132.txt")

print("--- %s seconds ---" % (time.time() - start_time))

# while True:
#     extension = fileName.split(".")[-1]
#     chunkName = fileName.split(".")[0] + str(file_number) + "."+extension
#     if path.exists(chunkFileName):
#         with open(chunkFileName) as f:
#             chunk = f.read()
#             with open(fileName, 'a') as merge_file:
#                 merge_file.write(chunk)
#             fileNumber+=1
#         os.remove(chunkFileName)
#     else:
#         break