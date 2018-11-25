import random
import time
import socket
import struct
from io import BytesIO


def unpack_bool(payload: BytesIO):
    return struct.unpack('?', payload.read(1))[0]


def unpack_char(payload: BytesIO):
    return struct.unpack('B', payload.read(1))[0]


def unpack_uint16(payload: BytesIO):
    return struct.unpack('<H', payload.read(2))[0]


def unpack_uint32(payload: BytesIO):
    return struct.unpack('<I', payload.read(4))[0]


def unpack_uint64(payload: BytesIO):
    return struct.unpack('<Q', payload.read(8))[0]


def pack_uint16(payload: int):
    return struct.pack('<H', payload)


def pack_uint32(payload: int):
    return struct.pack('<I', payload)


def pack_uint64(payload: int):
    return struct.pack('<Q', payload)


def pack_bool(payload: bool):
    return struct.pack('?', payload)


def pack_char(payload: int):
    return struct.pack('B', payload)


def ip2int(addr):
    return struct.unpack("!I", socket.inetaton(addr))[0]


def int2ip(addr):
    return socket.inetntoa(struct.pack("!I", addr))


def rshift(val, n):
    # 32bit rightshift
    return (val % 0x100000000) >> n


class Long:
    def __init__(self, val):
        """Looooooooooooooooooooooooooooooooooong"""
        if isinstance(val, int):
            if val > 0xffffffff:
                raise Exception("out of range")
        elif isinstance(val, bytes):
            _val = unpack_uint64(BytesIO(val))
            if _val > 0xffffffff:
                raise Exception("out of range")
        else:
            raise Exception("bad argument")
        self.val = val

    def to_bytes(self):
        if isinstance(self.val, int):
            return pack_uint64(self.val)
        return self.val

    def to_int(self):
        if isinstance(self.val, bytes):
            return unpack_uint64(BytesIO(self.val))
        return self.val
