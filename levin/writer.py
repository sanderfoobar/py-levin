from io import BytesIO

from levin.section import Section
from levin.exceptions import BadArgumentException
from levin.constants import *
from levin.ctypes import *


class LevinWriter:
    def __init__(self, buffer: BytesIO = None):
        self.buffer = buffer
        self._written = 0
        if not self.buffer:
            self.buffer = BytesIO()

    def write_payload(self, section):
        self.write(bytes(PORTABLE_STORAGE_SIGNATUREA))
        self.write(bytes(PORTABLE_STORAGE_SIGNATUREB))
        self.write(bytes(PORTABLE_STORAGE_FORMAT_VER))
        self.put_section(section)
        return self.buffer

    def put_section(self, section: Section):
        self.write_var_in(len(section))
        for k, v in section.entries.items():
            _k = k.encode('ascii')
            self.write(bytes(c_ubyte(len(_k))))
            self.write(_k)
            self.serialized_write(v)

    def write_section(self, section):
        self.write(bytes(SERIALIZE_TYPE_OBJECT))
        self.put_section(section)

    def serialized_write(self, data):
        _types = {
            c_uint64: SERIALIZE_TYPE_UINT64,
            c_int64: SERIALIZE_TYPE_INT64,
            c_uint32: SERIALIZE_TYPE_UINT32,
            c_int32: SERIALIZE_TYPE_INT32,
            c_uint16: SERIALIZE_TYPE_UINT16,
            c_int16: SERIALIZE_TYPE_INT16,
            c_string: SERIALIZE_TYPE_STRING,
            c_ubyte: SERIALIZE_TYPE_UINT8,
            c_byte: SERIALIZE_TYPE_INT8
        }

        if type(data) in _types:
            self.write(bytes(_types[type(data)]))

            if isinstance(data, c_string):
                self.write_var_in(len(data))

            self.write(bytes(data))
        elif isinstance(data, Section):
            self.write_section(data)
        else:
            raise BadArgumentException("Unable to cast input to serialized data")

    def write_var_in(self, i: int):
        # contrib/epee/include/storages/portable_storage_to_bin.h:pack_varint

        if i <= 63:
            out = (i << 2) | PORTABLE_RAW_SIZE_MARK_BYTE.value
            self.write(bytes(c_ubyte(out)))
        elif i <= 16383:
            out = (i << 2) | PORTABLE_RAW_SIZE_MARK_WORD.value
            self.write(bytes(c_uint16(out)))
        elif i <= 1073741823:
            out = (i << 2) | PORTABLE_RAW_SIZE_MARK_DWORD.value
            self.write(bytes(c_uint32(out)))
        else:
            if i > 4611686018427387903:
                raise BadArgumentException("failed to pack varint - too big amount")
            out = (i << 2) | PORTABLE_RAW_SIZE_MARK_INT64.value
            self.write(bytes(c_uint64(out)))

    def write(self, data, tt=None):
        self.buffer.write(data)
        self._written += len(data)
