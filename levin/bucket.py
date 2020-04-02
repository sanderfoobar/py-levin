import logging
import sys
import struct
import socket
from io import BytesIO

from levin.section import Section
from levin.constants import *
from levin.exceptions import BadArgumentException
from levin.ctypes import *

log = logging.getLogger()

class Bucket:
    def __init__(self):
        self.signature = LEVIN_SIGNATURE
        if self.signature != LEVIN_SIGNATURE:
            raise BadArgumentException('Bender\'s nightmare')

        self.cb = None
        self.return_data = None
        self.command = None
        self.return_code = None
        self.flags = None
        self.protocol_version = None
        self.payload_section = None

    @classmethod
    def create_request(cls, command: int, payload: bytes = None, section: Section = None):
        bucket = cls()

        bucket.return_data = c_bool(True)
        bucket.command = c_uint32(command)
        bucket.return_code = c_uint32(0)
        bucket.flags = LEVIN_PACKET_REQUEST
        bucket.protocol_version = LEVIN_PROTOCOL_VER_1

        if payload:
            bucket.cb = c_uint64(len(payload))
            bucket.payload_section = payload

        if section:
            bucket.payload_section = bytes(section)
            bucket.cb = c_uint64(len(bucket.payload_section))

        return bucket

    @classmethod
    def create_response(cls, command: int, payload: bytes, return_code: int):
        bucket = cls()
        bucket.cb = c_uint64(len(payload))
        bucket.return_data = c_bool(False)
        bucket.command = c_uint32(command)
        bucket.return_code = c_uint32(return_code)
        bucket.flags = LEVIN_PACKET_RESPONSE
        bucket.protocol_version = LEVIN_PROTOCOL_VER_1

    @staticmethod
    def create_handshake_request(
        my_port: int = 0,
        network_id: bytes = None,
        peer_id: bytes = b'\x41\x41\x41\x41\x41\x41\x41\x41',
    ):
        """
        Helper function to create a handshake request. Does not require
        parameters but you can use them to impersonate a legit node.
        :param my_port: defaults to 0
        :param network_id: defaults to mainnet
        :param peer_id:
        :param verbose:
        :return:
        """
        handshake_section = Section.handshake_request(peer_id=peer_id, network_id=network_id, my_port=my_port)
        bucket = Bucket.create_request(P2P_COMMAND_HANDSHAKE.value, section=handshake_section)

        log.debug(">> created packet '%s'" % P2P_COMMANDS[bucket.command])

        header = bucket.header()
        body = bucket.payload()
        return bucket

    @staticmethod
    def create_stat_info_request(
        peer_id: bytes = b"\x41\x41\x41\x41\x41\x41\x41\x41",
    ):
        stat_info_section = Section.stat_info_request(peer_id=peer_id)
        log.debug(stat_info_section.entries["proof_of_trust"].entries.keys())
        bucket = Bucket.create_request(
            P2P_COMMAND_REQUEST_STAT_INFO.value, section=stat_info_section
        )

        log.debug(">> created packet '%s'" % P2P_COMMANDS[bucket.command])
        return bucket

    @classmethod
    def from_buffer(cls, signature: c_uint64, sock: socket.socket):
        if isinstance(signature, bytes):
            signature = c_uint64(signature)
        # if isinstance(buffer, bytes):
        #     buffer = BytesIO(buffer)
        bucket = cls()
        bucket.signature = signature
        bucket.cb = c_uint64.from_buffer(sock)
        bucket.return_data = c_bool.from_buffer(sock)
        bucket.command = c_uint32.from_buffer(sock)
        bucket.return_code = c_int32.from_buffer(sock)
        bucket.flags = c_uint32.from_buffer(sock)
        bucket.protocol_version = c_uint32.from_buffer(sock)

        if bucket.signature != LEVIN_SIGNATURE:
            raise IOError("Bender's nightmare missing")

        if bucket.cb > LEVIN_DEFAULT_MAX_PACKET_SIZE:
            raise IOError("payload too large")

        if bucket.command.value not in P2P_COMMANDS:
            raise IOError("unregonized command: %d" % bucket.command.value)

        bucket.payload = sock.recv(bucket.cb.value)

        while len(bucket.payload) < bucket.cb.value:
            bufsize = 2048
            remaining = bucket.cb.value - len(bucket.payload)
            if remaining < bufsize:
                bufsize = remaining
            bucket.payload += sock.recv(bufsize)

        bucket.payload_section = None

        log.debug("<< received packet '%s'" % P2P_COMMANDS[bucket.command])

        from levin.reader import LevinReader
        bucket.payload_section = LevinReader(BytesIO(bucket.payload)).read_payload()

        log.debug("<< parsed packet '%s'" % P2P_COMMANDS[bucket.command])
        return bucket

    def header(self):
        return b''.join((
            bytes(LEVIN_SIGNATURE),
            bytes(self.cb),
            b'\x01' if self.return_data else b'\x00',
            bytes(self.command),
            bytes(self.return_code),
            bytes(self.flags),
            bytes(self.protocol_version)
        ))

    def payload(self):
        return self.payload_section

    def get_peers(self):
        # helper function to retreive peerlisting where buckets.command was 1001
        if self.command != 1001:
            raise Exception("Only handshake has peerlisting")

        peers = []

        if 'local_peerlist_new' not in self.payload_section.entries:
            return

        for peer in [e.entries for e in self.payload_section.entries['local_peerlist_new']]:
            if 'adr' not in peer or 'addr' not in peer['adr'].entries:
                continue

            addr = peer['adr'].entries['addr'].entries
            last_seen, m_ip, m_port = peer['last_seen'], addr['m_ip'], addr['m_port']

            # reinterpret m_ip as big endian
            m_ip = c_uint32(m_ip.to_bytes(), endian='big')

            peers.append({
                'last_seen': peer['last_seen'],
                'ip': m_ip,
                'port': m_port
            })

        # sort on last seen
        peers = sorted(peers, key=lambda k: k['last_seen'], reverse=True)
        return peers
