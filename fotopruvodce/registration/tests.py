import re
import time

import pytest
from django.contrib.auth.models import User

from fotopruvodce.registration.crypt import ReversedTimestampSigner, SignatureTooFresh

re_SIGNATURE = re.compile(b'fotopruvodce:[^"]+')


def test_reversed_timestamp_signer():
    s = ReversedTimestampSigner()
    signature = s.sign("fotopruvodce")

    # use a "fresh" signer like we do in views
    s = ReversedTimestampSigner()

    # test basic functionality with no time requirements
    s.unsign(signature, min_age=0)

    with pytest.raises(SignatureTooFresh):
        s.unsign(signature, min_age=15)


@pytest.mark.django_db
def test_antibot_check(client, settings):
    user_count = User.objects.count()
    resp = client.get("/registrace/")
    assert resp.status_code == 200

    signature = re_SIGNATURE.search(resp.content).group(0).decode("ascii")

    resp = client.post(
        "/registrace/",
        data={
            "username": "test1",
            "email": "test@example.com",
            "password1": "123456",
            "password2": "123456",
            "signature": signature,
        },
        follow=True,
    )
    assert resp.status_code == 200
    assert b"spam" in resp.content and b"nebyl" in resp.content
    assert User.objects.count() == user_count  # no new user

    # success
    settings.ANTIBOT_MIN_TIME = 0.1
    resp = client.get("/registrace/")
    assert resp.status_code == 200

    signature = re_SIGNATURE.search(resp.content).group(0).decode("ascii")
    time.sleep(0.1)
    resp = client.post(
        "/registrace/",
        data={
            "username": "test1",
            "email": "test@example.com",
            "password1": "123456",
            "password2": "123456",
            "signature": signature,
        },
        follow=True,
    )
    assert resp.status_code == 200
    assert b" byl " in resp.content
    assert User.objects.count() == user_count + 1  # new user created
