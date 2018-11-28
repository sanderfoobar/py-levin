class BadPortableStorageSignature(Exception):
    def __init__(self, msg=None):
        super(BadPortableStorageSignature, self).__init__(msg)


class BadArgumentException(Exception):
    def __init__(self, msg=None):
        super(BadArgumentException, self).__init__(msg)