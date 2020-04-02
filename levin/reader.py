import sys
from io import BytesIO

from levin.utils import rshift
from levin.exceptions import BadPortableStorageSignature
from levin.ctypes import *
from levin.constants import *


class LevinReader:
    def __init__(self, buffer: BytesIO):
        if isinstance(buffer, bytes):
            buffer = BytesIO(buffer)
        self.buffer = buffer

    def read_payload(self):
        sig1 = c_uint32.from_buffer(self.buffer)
        sig2 = c_uint32.from_buffer(self.buffer)
        sig3 = c_ubyte.from_buffer(self.buffer)

        if sig1 != PORTABLE_STORAGE_SIGNATUREA:
            raise BadPortableStorageSignature()
        elif sig2 != PORTABLE_STORAGE_SIGNATUREB:
            raise BadPortableStorageSignature()
        elif sig3 != PORTABLE_STORAGE_FORMAT_VER:
            raise BadPortableStorageSignature()

        return self.read_section()

    def read_section(self):
        from levin.section import Section
        section = Section()
        count = self.read_var_int()

        while count > 0:
            section_name = self.read_section_name()
            storage_entry = self.load_storage_entry()
            section.add(section_name, storage_entry)
            count -= 1

        return section

    def read_section_name(self) -> str:
        len_name = c_ubyte.from_buffer(self.buffer)
        name = self.buffer.read(len_name.value)
        return name.decode('ascii')

    def load_storage_entry(self):
        _type = c_ubyte.from_buffer(self.buffer)

        if (_type & SERIALIZE_FLAG_ARRAY) != 0:
            return self.load_storage_array_entry(_type)
        if _type == SERIALIZE_TYPE_ARRAY:
            return self.read_storage_entry_array_entry()
        else:
            return self.read_storage_entry(_type)

    def read_storage_entry(self, _type: int):
        return self.read(_type=_type)

    def load_storage_array_entry(self, _type: int):
        _type &= ~SERIALIZE_FLAG_ARRAY.value
        return self.read_array_entry(_type)

    def read_storage_entry_array_entry(self):
        _type = c_ubyte.from_buffer(self.buffer)

        if (_type & SERIALIZE_FLAG_ARRAY) != 0:
            raise IOError("wrong type sequences")

        return self.load_storage_array_entry(_type)

    def read_array_entry(self, _type: int):
        data = []
        size = self.read_var_int()

        while size > 0:
            data.append(self.read(_type=_type))
            size -= 1
        return data

    def read(self, _type: int = None, count: int = None):
        if isinstance(count, int):
            if count > sys.maxsize:
                raise IOError()
            _data = self.buffer.read(count)
            return _data

        if _type == SERIALIZE_TYPE_UINT64:
            return c_uint64.from_buffer(self.buffer)
        elif _type == SERIALIZE_TYPE_INT64:
            return c_int64.from_buffer(self.buffer)
        elif _type == SERIALIZE_TYPE_UINT32:
            return c_uint32.from_buffer(self.buffer)
        elif _type == SERIALIZE_TYPE_INT32:
            return c_int32.from_buffer(self.buffer)
        elif _type == SERIALIZE_TYPE_UINT16:
            return c_uint16.from_buffer(self.buffer)
        elif _type == SERIALIZE_TYPE_INT16:
            return c_int16.from_buffer(self.buffer)
        elif _type == SERIALIZE_TYPE_UINT8:
            return c_ubyte.from_buffer(self.buffer)
        elif _type == SERIALIZE_TYPE_INT8:
            return c_byte.from_buffer(self.buffer)
        elif _type == SERIALIZE_TYPE_OBJECT:
            return self.read_section()
        elif _type == SERIALIZE_TYPE_STRING:
            return self.read_byte_array()

    def read_byte_array(self, count: int = None):
        if not isinstance(count, int):
            count = self.read_var_int()
        return self.read(count=count)

    def read_var_int(self):
        b = c_ubyte.from_buffer(self.buffer)
        size_mask = b & PORTABLE_RAW_SIZE_MARK_MASK

        if size_mask == PORTABLE_RAW_SIZE_MARK_BYTE:
            v = rshift(b, 2)
        elif size_mask == PORTABLE_RAW_SIZE_MARK_WORD:
            v = rshift(self.read_rest(b, 1), 2)
        elif size_mask == PORTABLE_RAW_SIZE_MARK_DWORD:
            v = rshift(self.read_rest(b, 3), 2)
        elif size_mask == PORTABLE_RAW_SIZE_MARK_INT64:
            v = rshift(self.read_rest(b, 7), 2)
        else:
            raise IOError('invalid var_int')
        return v

    def read_rest(self, first_byte: int, _bytes: int):
        result = first_byte
        for i in range(0, _bytes):
            result += (c_ubyte.from_buffer(self.buffer) << 8)

        return result
