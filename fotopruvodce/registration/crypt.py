
from django.conf import settings

try:
    from Crypto.Cipher import AES
except ImportError:
    if not settings.DEBUG:
        raise
    AES = None

if AES:
    import binascii

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
else:
    def encode_ts(ts):
        if not isinstance(ts, str):
            ts = str(ts)
        return ts

    def decode_ts(data):
        try:
            return float(data)
        except Exception:
            return None
