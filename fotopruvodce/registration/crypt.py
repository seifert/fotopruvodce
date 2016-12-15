
import binascii

from Crypto.Cipher import AES

from django.conf import settings

_AES_KEY = settings.SECRET_KEY[:AES.block_size]
_AES_IV = settings.SECRET_KEY[-AES.block_size:]


def _get_cipher():
    return AES.new(_AES_KEY, AES.MODE_CBC, _AES_IV)


def encode_ts(ts):
    if not isinstance(ts, str):
        ts = str(ts)
    return binascii.b2a_hex(
        _get_cipher().encrypt(
            ts + (' ' * (AES.block_size - (len(ts) % AES.block_size)))
        )
    )


def decode_ts(data):
    try:
        return float(_get_cipher().decrypt(bytes.fromhex(data)).decode())
    except Exception:
        return None
