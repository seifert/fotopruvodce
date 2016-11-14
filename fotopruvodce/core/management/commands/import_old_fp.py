
from datetime import datetime, date, time
from functools import lru_cache

import pytz

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.validators import ValidationError, validate_email, validate_ipv46_address
from django.db import connections, transaction
from django.db.utils import IntegrityError

from fotopruvodce.discussion.models import Comment, AnonymousComment

User = get_user_model()


@lru_cache(maxsize=1024)
def get_user(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


@lru_cache(maxsize=1024)
def get_comment(id):
    try:
        return Comment.objects.get(id=id)
    except Comment.DoesNotExist:
        return None


class Command(BaseCommand):

    help = 'Imports data from old Fotopruvodce database'

    def add_arguments(self, parser):
        pass

    @transaction.atomic
    def handle(self, *args, **options):
        conn = connections['default']
        conn_old = connections['old']

        # Anonymous user for unregistered users
        try:
            anonymous_user = User.objects.get(username='Anonymous')
        except User.DoesNotExist:
            anonymous_user = User(
                username='Anonymous', is_active=False,
                is_staff=False, is_superuser=False)
            anonymous_user.save()

        with conn_old.cursor() as cursor_old:

            # Users
            self.stdout.write('Import users')
            counter = 0
            cursor_old.execute(
                'SELECT id, passwd, jmeno, prijmeni, email, info FROM lidi'
            )
            for row in cursor_old.fetchall():
                id, passwd, jmeno, prijmeni, email, info = row

                displayed_email = email
                try:
                    validate_email(email)
                except ValidationError:
                    email = ''

                try:
                    with transaction.atomic():
                        user = User(
                            username=id, first_name=jmeno, last_name=prijmeni,
                            email=email, is_active=True, is_staff=False,
                            is_superuser=False
                        )
                        user.save()
                        user.profile.description = info
                        user.profile.displayed_email = displayed_email
                        user.profile.old_password = passwd
                        user.profile.save()
                except IntegrityError as e:
                    self.stdout.write(self.style.ERROR('%s %r' % (e, row)))

                counter += 1

            self.stdout.write(self.style.SUCCESS(
                'Successfully imported %d rows' % counter))

            # Discussion
            self.stdout.write('Import discussion')
            counter = 0
            cursor_old.execute(
                'SELECT id, nazev, zprava, tatka, thread, autor, email, '
                'den, cas, ip, registered FROM clanky ORDER BY id'
            )
            # WHERE thread IN (137269, 137249)
            for row in cursor_old.fetchall():
                (id, nazev, zprava, tatka, thread, autor,
                 email, den, cas, ip, registered) = row

                # user
                if registered:
                    user = get_user(autor)
                    if not user:
                        self.stdout.write(self.style.ERROR(
                            "Comment {} - convert '{}' to anonymous user".format(id, autor)))
                        user = anonymous_user
                else:
                    user = anonymous_user
                # ip
                if ip:
                    try:
                        validate_ipv46_address(ip)
                    except ValidationError:
                        self.stdout.write(self.style.ERROR(
                            "Comment {} - invalid IP {}".format(id, ip)))
                        ip = '0.0.0.0'
                else:
                    ip = '0.0.0.0'
                # timestamp
                if den is None:
                    den = date(100, 1, 1)
                if cas is None:
                    cas = time.min
                timestamp = pytz.timezone(
                    "Europe/Prague"
                ).localize(
                    datetime.combine(den, cas), is_dst=None
                )
                # parent
                if tatka != id:
                    parent = get_comment(tatka)
                    if not parent:
                        self.stdout.write(self.style.ERROR(
                            "Comment {} - parent {} doesn't exist, "
                            "try to find thread".format(id, tatka)
                        ))
                        parent = get_comment(thread)
                        if not parent:
                            self.stdout.write(self.style.ERROR(
                                "Comment {} - make orphan".format(id)
                            ))
                            parent = None
                else:
                    parent = None

                comment = Comment(
                    id=id, title=nazev, content=zprava, timestamp=timestamp,
                    ip=ip, user=user, parent=parent)
                comment.save(force_insert=True)
                if user == anonymous_user:
                    anonymous = AnonymousComment(
                        comment=comment, author=autor, email=email)
                    anonymous.save()

                counter += 1
                if not counter % 1000:
                    self.stdout.write(str(counter))

            self.stdout.write(self.style.SUCCESS(
                'Successfully imported %d rows' % counter))
