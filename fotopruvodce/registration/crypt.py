
import datetime
import time

from django.core.signing import TimestampSigner, BadSignature
from django.utils import baseconv


class SignatureTooFresh(BadSignature):
    pass


class ReversedTimestampSigner(TimestampSigner):

    def unsign(self, value, min_age=None):
        result = super(TimestampSigner, self).unsign(value)
        value, timestamp = result.rsplit(self.sep, 1)
        timestamp = baseconv.base62.decode(timestamp)
        if min_age is not None:
            if isinstance(min_age, datetime.timedelta):
                min_age = min_age.total_seconds()
            # Check timestamp is not older than min_age
            age = time.time() - timestamp
            if age < min_age:
                raise SignatureTooFresh(
                    'Signature age %s < %s seconds' % (age, min_age))
        return value
