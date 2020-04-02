from time import time
import random
from io import BytesIO
from collections import OrderedDict

from levin.constants import *
from levin.ctypes import *


class Section:
    def __init__(self):
        self.entries = OrderedDict()

    def add(self, key: str, entry: object):
        self.entries[key] = entry

    def __len__(self):
        return len(self.entries.keys())

    @classmethod
    def from_byte_array(cls, buffer: BytesIO):
        from levin.reader import LevinReader
        x = LevinReader(buffer)
        section = x.read_payload()
        return section

    @classmethod
    def handshake_request(cls, my_port: int = 0, network_id: bytes = None, peer_id: bytes = None):
        if not network_id:
            network_id = bytes.fromhex("1230f171610441611731008216a1a110")  # mainnet
        if not peer_id:
            peer_id = random.getrandbits(64)

        section = cls()
        node_data = Section()
        # node_data.add("local_time", c_uint64(0x4141414141414141))
        node_data.add("local_time", c_uint64(int(time())))
        node_data.add("my_port", c_uint32(my_port))
        node_data.add("network_id", c_string(network_id))
        node_data.add("peer_id", c_uint64(peer_id))
        section.add("node_data", node_data)

        payload_data = Section()
        payload_data.add("cumulative_difficulty", c_uint64(1))
        payload_data.add("current_height", c_uint64(1))
        genesis_hash = bytes.fromhex("418015bb9ae982a1975da7d79277c2705727a56894ba0fb246adaabb1f4632e3")  # genesis
        payload_data.add("top_id", c_string(genesis_hash))
        payload_data.add("top_version", c_ubyte(1))
        section.add("payload_data", payload_data)
        return section

    @classmethod
    def create_flags_response(cls):
        section = cls()
        section.add("support_flags", P2P_SUPPORT_FLAGS)
        return section

    @classmethod
    def stat_info_request(cls, peer_id: bytes = None):
        if not peer_id:
            peer_id = random.getrandbits(64)

        signature = bytes.fromhex(
            "418015bb9ae982a1975da7d79277c2705727a56894ba0fb246adaabb1f4632e3"
        )

        section = cls()
        proof_of_trust = Section()
        proof_of_trust.add("peer_id", c_uint64(peer_id))
        proof_of_trust.add("time", c_uint64(int(time())))
        proof_of_trust.add("sign", c_string(signature))

        section.add("proof_of_trust", proof_of_trust)

        return section

    def __bytes__(self):
        from levin.writer import LevinWriter

        writer = LevinWriter()
        buffer = writer.write_payload(self)
        buffer.seek(0)
        return buffer.read()
