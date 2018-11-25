import random
import time

from levin import Section
from levin.utils import Long
from levin.constants import *


def create_handshake_request(my_port: int = 0, network_id: bytes = None):
    if not network_id:
        network_id = bytearray.fromhex("1230f171610441611731008216a1a110")  # mainnet
    section = Section()

    node_data = Section()
    node_data.add("local_time", int(time.time()))
    node_data.add("my_port", my_port)
    node_data.add("network_id", network_id)
    node_data.add("peer_id", random.getrandbits(64))
    section.add("node_data", node_data)

    payload_data = Section()
    payload_data.add("cumulative_difficulty", Long(1))
    payload_data.add("current_height", Long(1))
    genesis_hash = bytearray.fromhex("418015bb9ae982a1975da7d79277c2705727a56894ba0fb246adaabb1f4632e3")  # genesis
    payload_data.add("top_id", genesis_hash)
    payload_data.add("top_version", b"\x01")
    section.add("payload_data", payload_data)
    return section


def create_flags_response():
    section = Section()
    section.add("support_flags", P2P_SUPPORT_FLAGS)
    return section
