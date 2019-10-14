fileName = raw_input("Enter fileName you want to break into chunks")
CHUNK_SIZE = raw_input("Enter the chunk size ")
file_number = 1

with open(fileName) as f:
    chunk = f.read(CHUNK_SIZE)
    while chunk:
        with open(fileName + str(file_number)) as chunk_file:
            chunk_file.write(chunk)
        file_number += 1
        chunk = f.read(CHUNK_SIZE)