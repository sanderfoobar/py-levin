from io import BytesIO
from collections import OrderedDict


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

    def as_byte_array(self):
        from levin.writer import LevinWriter

        buffer = BytesIO()
        writer = LevinWriter(buffer)
        writer.write_payload(self)
