import random
import time
import socket
import ipaddress
import struct
from io import BytesIO


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
    return ipaddress.IPv4Address(addr)


def rshift(val, n):
    # 32bit rightshift
    return (val % 0x100000000) >> n
