from levin.ctypes import *

LEVIN_OK = c_ubyte(0x00)
LEVIN_SIGNATURE = c_uint64(0x0101010101012101)  # Bender's nightmare
LEVIN_PACKET_REQUEST = c_uint32(0x00000001)
LEVIN_PACKET_RESPONSE = c_uint32(0x00000002)
LEVIN_DEFAULT_MAX_PACKET_SIZE = 100000000  # 100MB
LEVIN_PROTOCOL_VER_1 = c_uint32(1)
LEVIN_ERROR_CONNECTION = -1
LEVIN_ERROR_CONNECTION_NOT_FOUND = -2
LEVIN_ERROR_CONNECTION_DESTROYED = -3
LEVIN_ERROR_CONNECTION_TIMEDOUT = -4
LEVIN_ERROR_CONNECTION_NO_DUPLEX_PROTOCOL = -5
LEVIN_ERROR_CONNECTION_HANDLER_NOT_DEFINED = -6
LEVIN_ERROR_FORMAT = -7

P2P_SUPPORT_FLAG_FLUFFY_BLOCKS = c_ubyte(0x01)
P2P_SUPPORT_FLAGS = P2P_SUPPORT_FLAG_FLUFFY_BLOCKS
P2P_COMMANDS_POOL_BASE = c_uint32(1000)
P2P_COMMAND_HANDSHAKE = c_uint32(P2P_COMMANDS_POOL_BASE + 1)  # carries payload
P2P_COMMAND_TIMED_SYNC = c_uint32(P2P_COMMANDS_POOL_BASE + 2)  # carries payload
P2P_COMMAND_PING = c_uint32(P2P_COMMANDS_POOL_BASE + 3)
P2P_COMMAND_REQUEST_STAT_INFO = c_uint32(P2P_COMMANDS_POOL_BASE + 4)
P2P_COMMAND_REQUEST_NETWORK_STATE = c_uint32(P2P_COMMANDS_POOL_BASE + 5)
P2P_COMMAND_REQUEST_PEER_ID = c_uint32(P2P_COMMANDS_POOL_BASE + 6)
P2P_COMMAND_REQUEST_SUPPORT_FLAGS = c_uint32(P2P_COMMANDS_POOL_BASE + 7)
P2P_COMMANDS = {
    P2P_COMMAND_HANDSHAKE: 'handshake',
    P2P_COMMAND_TIMED_SYNC: 'timed_sync',
    P2P_COMMAND_PING: 'ping',
    P2P_COMMAND_REQUEST_SUPPORT_FLAGS: 'support_flags',
    P2P_COMMAND_REQUEST_STAT_INFO: 'stat_info',
    P2P_COMMAND_REQUEST_NETWORK_STATE: 'network_state',
    P2P_COMMAND_REQUEST_PEER_ID: 'peer_id',
}

PORTABLE_STORAGE_SIGNATUREA = c_uint32(0x01011101)
PORTABLE_STORAGE_SIGNATUREB = c_uint32(0x01020101)
PORTABLE_STORAGE_FORMAT_VER = c_ubyte(1)
PORTABLE_RAW_SIZE_MARK_MASK = c_ubyte(3)
PORTABLE_RAW_SIZE_MARK_BYTE = c_ubyte(0)
PORTABLE_RAW_SIZE_MARK_WORD = c_ubyte(1)
PORTABLE_RAW_SIZE_MARK_DWORD = c_ubyte(2)
PORTABLE_RAW_SIZE_MARK_INT64 = c_ubyte(3)

MAX_STRING_LEN_POSSIBLE = 2000000000  # do not let string be so big

# data types (boost serialization)
SERIALIZE_TYPE_INT64 = c_ubyte(1)
SERIALIZE_TYPE_INT32 = c_ubyte(2)
SERIALIZE_TYPE_INT16 = c_ubyte(3)
SERIALIZE_TYPE_INT8 = c_ubyte(4)
SERIALIZE_TYPE_UINT64 = c_ubyte(5)
SERIALIZE_TYPE_UINT32 = c_ubyte(6)
SERIALIZE_TYPE_UINT16 = c_ubyte(7)
SERIALIZE_TYPE_UINT8 = c_ubyte(8)
SERIALIZE_TYPE_DOUBLE = c_ubyte(9)
SERIALIZE_TYPE_STRING = c_ubyte(10)
SERIALIZE_TYPE_BOOL = c_ubyte(11)
SERIALIZE_TYPE_OBJECT = c_ubyte(12)
SERIALIZE_TYPE_ARRAY = c_ubyte(13)
SERIALIZE_FLAG_ARRAY = c_ubyte(0x80)

# (src/p2p/net_node.inl:715 in node_server::get_ip_seed_nodes)
SEED_NODES = [
    ("212.83.175.67", 18080),
    ("212.83.172.165", 18080),
    ("176.9.0.187", 18080),
    ("88.198.163.90", 18080),
    ("95.217.25.101", 18080),
    ("136.244.105.131", 18080),
    ("104.238.221.81", 18080),
    ("66.85.74.134", 18080),
    ("88.99.173.38", 18080),
    ("51.79.173.165", 18080)
]
