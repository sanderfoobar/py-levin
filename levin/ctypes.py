import socket
import struct
import ipaddress
from io import BytesIO
from datetime import datetime
from ctypes import (
    c_ushort as _c_ushort,
    c_ubyte as _c_ubyte,
    c_uint8 as _c_uint8,
    c_uint16 as _c_uint16,
    c_uint32 as _c_uint32,
    c_uint64 as _c_uint64,
    c_short as _c_short,
    c_byte as _c_byte,
    c_int8 as _c_int8,
    c_int16 as _c_int16,
    c_int32 as _c_int32,
    c_int64 as _c_int64,
)

from levin.exceptions import BadArgumentException


class _CType:
    def __init__(self, value, endian=None):
        self.value = value
        self.endian = endian

    @classmethod
    def from_buffer(cls, buffer, endian: str = 'little', padding: bytes = None):
        if isinstance(buffer, BytesIO):
            buffer = buffer.read(cls.NBYTES)
        elif isinstance(buffer, socket.socket):
            buffer = buffer.recv(cls.NBYTES)

        if len(buffer) < cls.NBYTES:
            if not padding:
                _bytes = 'bytes' if cls.NBYTES > 1 else 'byte'
                raise BadArgumentException("requires a buffer of %d %s, received %d" % (cls.NBYTES, _bytes, len(buffer)))

            func_padding = bytes.ljust if endian == 'little' else bytes.rjust
            buffer = func_padding(buffer, cls.NBYTES, padding)

        _endian = '<' if endian == 'little' else '>'
        type_struct = cls.TYPE_STRUCT if hasattr(cls, 'TYPE_STRUCT') else cls.TYPE._type_
        value = struct.unpack('%s%s' % (_endian, type_struct), buffer)[0]
        return cls(value, endian)

    def to_bytes(self):
        if isinstance(self.value, (int, bool)):
            type_struct = self.TYPE_STRUCT if hasattr(self, 'TYPE_STRUCT') else self.TYPE._type_
            return struct.pack('%s%s' % ('<' if self.endian == 'little' else '>', type_struct), self.value)
        elif isinstance(self.value, bytes):
            if self.endian == 'little':
                return self.value[::-1]
            return self.value

    def _overflows(self):
        if isinstance(self.value, int):
            try:
                self.value.to_bytes(self.NBYTES, byteorder=self.endian, signed=self.SIGNED)
            except OverflowError as e:
                raise OverflowError("Value \'%d\' does not fit in %s." % (self.value, self.__class__.__name__))

    def __len__(self):
        if isinstance(self.value, bytes):
            return len(self.value)
        if isinstance(self.value, int):
            return len(bytes(self))

        return len(bytes(self.value))

    def __eq__(self, other):
        if isinstance(self.value, int):
            return self.value == other

    def __ne__(self, other):
        if isinstance(other, _CType):
            other = other.value

        if isinstance(self.value, int):
            return self.value != other

    def __and__(self, other):
        if isinstance(other, _CType):
            other = other.value

        if isinstance(self.value, int):
            # Bitwise AND
            return self.value & other
        raise NotImplementedError()

    def __lshift__(self, other):
        if isinstance(other, _CType):
            other = other.value

        if isinstance(self.value, int):
            # Bitwise Left Shift
            return self.value << other
        raise NotImplementedError()

    def __rshift__(self, other):
        if isinstance(other, _CType):
            other = other.value

        if isinstance(self.value, int):
            # Bitwise Right Shift
            return self.value >> other
        raise NotImplementedError()

    def __rlshift__(self, other):
        if isinstance(other, _CType):
            other = other.value

        if isinstance(self.value, int):
            # Bitwise Right Shift
            return self.value << other
        raise NotImplementedError()

    def __rrshift__(self, other):
        if isinstance(other, _CType):
            other = other.value

        if isinstance(self.value, int):
            # Bitwise Left Shift
            return self.value >> other
        raise NotImplementedError()

    def __or__(self, other):
        if isinstance(other, _CType):
            other = other.value

        if isinstance(self.value, int):
            # Bitwise OR
            return self.value | other
        raise NotImplementedError()

    def __mod__(self, other):
        if isinstance(other, _CType):
            other = other.value

        if isinstance(self.value, int):
            return self.value % other

    def __add__(self, other):
        if isinstance(other, _CType):
            other = other.value

        if isinstance(self.value, int):
            return self.value + other

    def __radd__(self, other):
        if isinstance(other, _CType):
            other = other.value

        if isinstance(self.value, int):
            return self.value + other

    def __gt__(self, other):
        if isinstance(other, _CType):
            other = other.value

        if isinstance(self.value, int):
            return self.value > other

    def __lt__(self, other):
        if isinstance(other, _CType):
            other = other.value

        if isinstance(self.value, int):
            return self.value < other

    def __bytes__(self):
        return self.to_bytes()

    def __hash__(self):
        return self.value

    def __int__(self):
        return self.value


class _IntType(_CType):
    def __init__(self, value, endian='little'):
        super(_IntType, self).__init__(value, endian)
        self._overflows()

    def __repr__(self):
        _signed = 'unsigned' if not self.SIGNED else 'signed'
        _bytes = 'bytes' if self.NBYTES > 1 else 'byte'
        _cls_name = self.__class__.__name__
        return '\'%d\' - %s - %s %d %s' % (self.value, _cls_name, _signed, self.NBYTES, _bytes)


class c_int16(_IntType):
    TYPE = _c_short
    NBYTES = 2
    SIGNED = True

    def __init__(self, value, endian='little'):
        super(c_int16, self).__init__(value, endian)


class c_uint16(_IntType):
    TYPE = _c_ushort
    NBYTES = 2
    SIGNED = False

    def __init__(self, value, endian='little'):
        super(c_uint16, self).__init__(value, endian)


class c_int32(_IntType):
    TYPE = _c_uint32
    NBYTES = 4
    SIGNED = True

    def __init__(self, value, endian='little'):
        super(c_int32, self).__init__(value, endian)


class c_uint32(_IntType):
    TYPE = _c_uint32
    NBYTES = 4
    SIGNED = False

    def __init__(self, value, endian='little'):
        super(c_uint32, self).__init__(value, endian)

    @property
    def ipv4(self) -> str:
        return str(ipaddress.IPv4Address(self.value))

    @property
    def ip(self) -> str:
        return self.ipv4


class c_int64(_IntType):
    TYPE = _c_uint64
    TYPE_STRUCT = 'q'
    NBYTES = 8
    SIGNED = True

    def __init__(self, value, endian='little'):
        super(c_int64, self).__init__(value, endian)

    @property
    def date_utc(self):
        return datetime.utcfromtimestamp(self.value)


class c_uint64(_IntType):
    TYPE = _c_uint64
    TYPE_STRUCT = 'Q'
    NBYTES = 8
    SIGNED = False

    def __init__(self, value, endian='little'):
        super(c_uint64, self).__init__(value, endian)

    @property
    def ipv6(self) -> str:
        val = socket.inet_ntop(socket.AF_INET6, self.value)
        if val.startswith("::ffff:"):
            val = val[7:]
        return val

    @property
    def ip(self) -> str:
        return self.ipv6

    @property
    def date_utc(self):
        return datetime.utcfromtimestamp(self.value)


class c_byte(_IntType):
    TYPE = _c_byte
    NBYTES = 1
    SIGNED = True

    def __init__(self, value, endian='little'):
        super(c_byte, self).__init__(value, endian)


class c_bytes(_CType):
    def __init__(self, value, endian='little'):
        super(c_bytes, self).__init__(value, endian)


class c_ubyte(_IntType):
    TYPE = _c_ubyte
    NBYTES = 1
    SIGNED = False

    def __init__(self, value, endian='little'):
        super(c_ubyte, self).__init__(value, endian)


class c_string(_CType):
    ENCODING = 'ascii'

    def __init__(self, value):
        super(c_string, self).__init__(value)
        if isinstance(value, bytes):
            self.NBYTES = len(value)
        else:
            self.NBYTES = len(self.value.encode(self.ENCODING))


class c_bool(_CType):
    TYPE_STRUCT = '?'
    NBYTES = 1

    def __init__(self, value, endian=None):
        if value not in [True, False]:
            raise BadArgumentException('bool')
        super(c_bool, self).__init__(value)
