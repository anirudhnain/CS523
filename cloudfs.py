import boto3
from functools import lru_cache

BUCKET = 'speedfs'
BLOCKSIZE = 8192


class CloudFileSystem(object):
    def __init__(self, client):
        self.s3 = client

    def list_files(self, prefix):
        pass


def get_directories(s3, bucket, path=""):
    response = s3.list_objects_v2(Bucket=bucket,
                                  Prefix=path,
                                  Delimiter="/")
    if response is None:
        return
    if 'CommonPrefixes' in response:
        for v in response['CommonPrefixes'][0].values():
            yield v


def get_files(s3, bucket, path=""):
    continuation_token = ''
    while True:
        kwargs = {'Bucket': bucket,
                  'Prefix': path,
                  'Delimiter': "/"}
        if continuation_token:
            kwargs["ContinuationToken"] = continuation_token

        response = s3.list_objects_v2(**kwargs)
        if response is None:
            return

        continuation_token = response.get('NextContinuationToken', None)
        if 'Contents' in response:
            for obj in response['Contents']:
                yield obj
        if not response.get('IsTruncated', False):
            break


def write_file(s3, bucket, path, data):
    s3.put_object(Bucket=bucket,
                  Body=data,
                  Key=path)


def read_file(s3, bucket, path):
    response = s3.get_object(Bucket=bucket,
                             Key=path)
    if response:
        return response['Body'].read()
    return None


@lru_cache()
def get_client():
    return boto3.client('s3')


def get_bucket():
    return BUCKET


def get_cache_dir():
    return "/tmp/cache"


class FileNode(object):
    def __init__(self, path, is_directory=False,
                 children=None, size=0):
        self.is_directory = is_directory
        self.children = children if children else []
        self.path = path
        self.size = size


class Node(object):
    def __init__(self, path):
        self.num_blocks = 0
        self.blocks = []
        self.path = path
        self.total_size = 0
        self.load_metadata(path)
        self.block_size = 8192

    def load_metadata(self, path):
        files = [_ for _ in get_files(get_client(),
                                      get_bucket(),
                                      path + "/")]
        self.num_blocks = len(files)
        self.total_size = sum(x['Size'] for x in files)
        self.blocks = sorted([x['Key'] for x in files],
                             key=lambda x: int(x.split("/")[-1]))

    def read_block(self, i):
        assert 0 <= i < self.num_blocks
        return read_file(get_client(), get_bucket(), self.blocks[i])

    def _append_block(self, data):
        self.blocks.append(self.path + "/" + str(self.num_blocks))
        write_file(get_client(), get_bucket(),
                   self.blocks[-1],
                   data)
        self.num_blocks += 1

    def write_block(self, i, data):
        assert i >= 0
        start = 0
        if i >= self.num_blocks:
            self._append_block(data[start:start + self.block_size])
        else:
            write_file(get_client(), get_bucket(),
                       self.blocks[i], data)

    def read(self, offset, size):
        block = offset // self.block_size
        end_offset = min(self.total_size, offset + size,
                         (block + 1) * self.block_size)

        offset -= block * self.block_size
        end_offset -= block * self.block_size
        return self.read_block(block)[offset:end_offset]

    def write(self, offset, data):
        if offset >= self.total_size and len(data) != 0:
            self.write(self.total_size, b'0' * (offset - self.total_size))
        block = offset // self.block_size
        base = block * self.block_size
        base_offset = offset % self.block_size
        end = min(offset + len(data), base + self.block_size)

        if base_offset != 0:
            if block < self.num_blocks:
                temp = self.read_block(block)
            else:
                temp = '\x00' * self.block_size
                if block == self.num_blocks - 1:
                    temp = temp[:max(self.total_size % self.block_size,
                                     base_offset)]

            return self.write(base, temp[:base_offset] + data) - base_offset

        if block == self.num_blocks - 1 and end < self.total_size:
            temp = self.read_block(self.num_blocks - 1)
            return self.write(base, data + temp[end - base:]) - base

        self.write_block(block, data[:end - base])
        return end - base


def load_fs(s3, bucket, path):
    files = [_ for _ in get_files(s3, bucket, path)]
    directories = [_ for _ in get_directories(s3, bucket, path)]

    dir_nodes = [load_fs(s3, bucket, directory) for directory in
                 directories]
    file_nodes = [FileNode(file['Key'], is_directory=False, size=file['Size'])
                  for file in files]
    return FileNode(path, is_directory=True, children=file_nodes + dir_nodes)


def print_tree(node):
    print(node.path)
    if node.is_directory:
        for child in node.children:
            print_tree(child)


if __name__ == "__main__":
    n = Node("file2")
    print(n.read(0, 8))
