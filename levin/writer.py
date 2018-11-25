from io import BytesIO

from levin.section import Section
from levin.utils import (
    pack_uint32, pack_uint16, pack_uint64, pack_char, Long
)
from levin.constants import *


class BadArgumentException(Exception):
    def __init__(self, msg=None):
        super(BadArgumentException, self).__init__(msg)


class LevinWriter:
    def __init__(self, buffer: BytesIO = None):
        self.buffer = buffer
        if not self.buffer:
            self.buffer = BytesIO()

    def write_payload(self, section):
        self.write(pack_uint32(PORTABLE_STORAGE_SIGNATUREA))
        self.write(pack_uint32(PORTABLE_STORAGE_SIGNATUREB))
        self.write(pack_char(PORTABLE_STORAGE_FORMAT_VER))
        self.put_section(section)

    def put_section(self, section: Section):
        self.write_var_in(len(section))
        for k, v in section.entries.items():
            _k = k.encode('ascii')
            self.write(pack_char(len(_k)))  # TODO: check length?
            self.write(_k)
            self.serialized_write(v)

    def write_section(self, section):
        self.write(pack_char(SERIALIZE_TYPE_OBJECT))
        self.put_section(section)

    def serialized_write(self, inp):
        if isinstance(inp, bytes):
            self.write(pack_char(SERIALIZE_TYPE_STRING))
            self.write_var_in(len(inp))  # @TODO: double check if length is oki
            self.write(inp)
        elif isinstance(inp, str):
            val = inp.encode('ascii')
            self.write(pack_char(SERIALIZE_TYPE_STRING))
            self.write_var_in(len(inp))  # @TODO: double check if length is oki
            self.write(val)
        elif isinstance(inp, Long):
            self.write(pack_char(SERIALIZE_TYPE_UINT64))
            self.write(pack_uint64(inp.to_int()))
        elif isinstance(inp, int) and inp <= 0xFF:
            self.write(pack_char(SERIALIZE_TYPE_UINT8))
            self.write(pack_char(inp))
        elif isinstance(inp, int) and inp <= 0xffffffff:
            self.write(pack_char(SERIALIZE_TYPE_UINT32))
            self.write(pack_uint32(inp))
        elif isinstance(inp, int):
            self.write(pack_char(SERIALIZE_TYPE_UINT64))
            self.write(pack_uint64(inp))
        elif isinstance(inp, Section):
            self.write_section(inp)
        else:
            raise BadArgumentException("Unable to cast input to serialized data")

    def write_var_in(self, i: int):
        if i <= 63:
            out = (i << 2) | PORTABLE_RAW_SIZE_MARK_BYTE
            self.write(pack_char(out))
        elif i <= 16383:
            out = (i << 2) | PORTABLE_RAW_SIZE_MARK_WORD
            self.write(pack_uint16(out))
        elif i <= 1073741823:
            out = (i << 2) | PORTABLE_RAW_SIZE_MARK_DWORD
            self.write(pack_uint32(out))
        else:
            if i > 4611686018427387903:
                raise BadArgumentException("bad value")
            out = (i << 2) | PORTABLE_RAW_SIZE_MARK_INT64
            self.write(pack_uint64(out))
    
    def write(self, data):
        self.buffer.write(data)
