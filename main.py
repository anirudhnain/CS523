from __future__ import print_function, absolute_import, division

import logging
from stat import S_IFDIR, S_IFREG
from time import time
from errno import ENOENT, ENOTTY

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from cloudfs import get_bucket, get_client, get_directories, Node

if not hasattr(__builtins__, 'bytes'):
    bytes = str


class CloudFS(LoggingMixIn, Operations):
    def __init__(self):
        self.files = {}
        self.data = {}
        self.fd = 0
        now = time()
        self.files['/'] = dict(
            st_mode=(S_IFDIR | 0o777),
            st_ctime=now,
            st_mtime=now,
            st_atime=now,
            st_nlink=2
        )

        for directory in get_directories(get_client(), get_bucket(), ""):
            directory = directory[:-1]
            # print("Directory: \n\n\n\n" + directory + "\n\n\n")

            self.data["/" + directory] = node = Node(directory)
            self.files["/" + directory] = dict(
                st_mode=(S_IFREG | 0o777),
                st_size=node.total_size,
                st_ctime=now,
                st_mtime=now,
                st_atime=now,
                st_nlink=2
            )

    def create(self, path, mode):
        self.files[path] = dict(
            st_mode=(S_IFREG | mode),
            st_nlink=1,
            st_size=0,
            st_ctime=time(),
            st_mtime=time(),
            st_atime=time())

        self.fd += 1
        return self.fd

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def getattr(self, path, fh=None):
        print(path)
        if path not in self.files:
            raise FuseOSError(ENOENT)

        return self.files[path]

    def chmod(self, path, mode):
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        return self.data[path].read(offset, size)

    def write(self, path, data, offset, fh):
        result = self.data[path].write(offset, data)
        self.files[path]['st_size'] = self.data[path].total_size
        return result

    def readdir(self, path, fh):
        return ['.', '..'] + [x[1:] for x in self.files if x != '/']

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    def getxattr(self, path, name, position=0):
        attrs = self.files[path].get('attrs', {})

        try:
            return attrs[name]
        except KeyError:
            return ''  # Should return ENOATTR

    def listxattr(self, path):
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('mount')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(CloudFS(), args.mount, foreground=True, allow_other=True)
