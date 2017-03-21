import os
import struct
import time
import base64


def generate_auth_key():
    """
    Generates a secret key to be used in ceph cluster keyring.

    It generates a base64 encoded string out of a byte string
    created by packing random data into struct. This is used
    while cluster creation as keyring secret key
    """

    key = os.urandom(16)
    header = struct.pack(
        '<hiih',
        1,                 # le16 type: CEPH_CRYPTO_AES
        int(time.time()),  # le32 created: seconds
        0,                 # le32 created: nanoseconds,
        len(key),          # le16: len(key)
    )
    return base64.b64encode(header + key).decode('utf-8')
