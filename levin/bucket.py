import sys
import struct
from io import BytesIO

from levin.constants import *
from levin.utils import pack_uint64, unpack_uint64, unpack_uint32, unpack_char, unpack_bool


class Bucket:
    def __init__(self, buffer: BytesIO):
        from levin.reader import LevinReader
        buffer.seek(0)

        self.signature = unpack_uint64(buffer)
        self.cb = unpack_uint64(buffer)
        self.return_data = unpack_bool(buffer)
        self.command = unpack_uint32(buffer)
        self.return_code = unpack_uint32(buffer)
        self.flags = unpack_uint32(buffer)
        self.protocol_version = unpack_uint32(buffer)
    
        if self.signature != LEVIN_SIGNATURE:
            raise IOError("Bender's nightmare missing")

        if self.cb > sys.maxsize:
            raise IOError("int too large")

        buffer = buffer.read(self.cb)
        self.payload_section = LevinReader.read_payload(buffer)

    @classmethod
    def create_request(cls, command: int, payload: bytes):
        cls.signature = LEVIN_SIGNATURE
        cls.cb = len(payload)
        cls.return_data = True
        cls.command = command
        cls.return_code = 0
        cls.flags = LEVIN_PACKET_REQUEST
        cls.protocol_version = LEVIN_PROTOCOL_VER_1

    @classmethod
    def create_response(cls, command: int, payload: bytes, rc: int):
        cls.signature = LEVIN_SIGNATURE
        cls.cb = len(payload)
        cls.return_data = False
        cls.command = command
        cls.return_code = rc
        cls.flags = LEVIN_PACKET_RESPONSE
        cls.protocol_version = LEVIN_PROTOCOL_VER_1

    def get_header(self):
        return b''.join((
            pack_uint64(self.signature),
            pack_uint64(self.cb),
            b'\x01' if self.return_data else b'\x00',
            struct.pack('<i', self.command),
            struct.pack('<i', self.return_code),
            struct.pack('<i', self.flags),
            struct.pack('<I', self.protocol_version))
        )
