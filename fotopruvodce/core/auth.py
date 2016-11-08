
import crypt
import logging

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class OldFotopruvodceBackend(object):

    def authenticate(self, username=None, password=None):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass
        else:
            if not user.password and user.profile.old_password:
                if user.profile.old_password == crypt.crypt(password, username[:2]):
                    logger.info("Convert password for user '%s'", username)
                    user.set_password(password)
                    user.save()
                    return user
        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
