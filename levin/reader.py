import sys
from io import BytesIO

from levin.utils import (
    rshift, unpack_char, unpack_uint16,
    unpack_uint32, unpack_uint64
)
from levin.constants import *


class BadPortableStorageSignature(Exception):
    def __init__(self, msg=None):
        super(BadPortableStorageSignature, self).__init__(msg)


class LevinReader:
    def __init__(self, payload: BytesIO):
        self.payload = payload

    def read_payload(self):
        sig1 = unpack_uint32(self.payload)
        sig2 = unpack_uint32(self.payload)
        sig3 = unpack_char(self.payload)

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
        len_name = unpack_char(self.payload)
        name = self.payload.read(len_name)
        return name.decode('ascii')

    def load_storage_entry(self):
        _type = unpack_char(self.payload)

        if (_type & SERIALIZE_FLAG_ARRAY) != 0:
            return self.load_storage_array_entry(_type)
        if _type == SERIALIZE_TYPE_ARRAY:
            return self.read_storage_entry_array_entry()
        else:
            return self.read_storage_entry(_type)

    def read_storage_entry(self, _type: int):
        return self.read(_type=_type)

    def load_storage_array_entry(self, _type: int):
        _type &= ~SERIALIZE_FLAG_ARRAY
        return self.read_array_entry(_type)

    def read_storage_entry_array_entry(self):
        _type = unpack_char(self.payload)

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
            _data = self.payload.read(count)
            return _data

        if _type == SERIALIZE_TYPE_UINT64 or _type == SERIALIZE_TYPE_INT64:
            return unpack_uint64(self.payload)
        elif _type == SERIALIZE_TYPE_UINT32 or _type == SERIALIZE_TYPE_INT32:
            return unpack_uint32(self.payload)
        elif _type == SERIALIZE_TYPE_UINT16 or _type == SERIALIZE_TYPE_INT16:
            return unpack_uint16(self.payload)
        elif _type == SERIALIZE_TYPE_UINT8 or _type == SERIALIZE_TYPE_INT8:
            return unpack_char(self.payload)
        elif _type == SERIALIZE_TYPE_OBJECT:
            return self.read_section()
        elif _type == SERIALIZE_TYPE_STRING:
            return self.read_byte_array()

    def read_byte_array(self, count: int = None):
        if not isinstance(count, int):
            count = self.read_var_int()
        return self.read(count=count)

    def read_var_int(self):
        b = unpack_char(self.payload)
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
            result += (unpack_char(self.payload) << 8)

        return result
