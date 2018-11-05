import os
import struct

from bsplayer.exceptions import SizeTooSmallError


class VideoInfo:
    LITTLE_ENDIAN_LONG_LONG = '<q'
    BYTE_SIZE = struct.calcsize(LITTLE_ENDIAN_LONG_LONG)

    def __init__(self, video_path):
        self.path = video_path
        self._video_stat = os.stat(video_path)
        self.size = self._video_stat.st_size
        self._hash = None

    @property
    def hash(self):
        if self._hash:
            return self._hash

        self._hash = self.size
        if self.size < 65536 * 2:
            raise SizeTooSmallError('Size too small')

        with open(self.path, 'rb') as fd:
            for x in range(65536 // self.BYTE_SIZE):
                buff = fd.read(self.BYTE_SIZE)
                (l_value,) = struct.unpack(self.LITTLE_ENDIAN_LONG_LONG, buff)
                self._hash += l_value
                self._hash &= 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number

            fd.seek(max(0, self.size - 65536), 0)
            for x in range(65536 // self.BYTE_SIZE):
                buff = fd.read(self.BYTE_SIZE)
                (l_value,) = struct.unpack(self.LITTLE_ENDIAN_LONG_LONG, buff)
                self._hash += l_value
                self._hash &= 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number

        self._hash = '%016x' % self._hash
        return self._hash
