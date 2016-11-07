
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.validators import ValidationError, validate_email
from django.db import connections, transaction
from django.db.utils import IntegrityError


class Command(BaseCommand):

    help = 'Imports data from old Fotopruvodce database'

    def add_arguments(self, parser):
        pass

    @transaction.atomic
    def handle(self, *args, **options):
        user_cls = get_user_model()
        conn = connections['default']
        conn_old = connections['old']

        with conn.cursor() as cursor:
            cursor.execute(
                'ALTER TABLE auth_user MODIFY username varchar(150) '
                'CHARACTER SET utf8 COLLATE utf8_bin'
            )

        with conn_old.cursor() as cursor_old:
            counter = 0
            cursor_old.execute(
                'SELECT id, passwd, jmeno, prijmeni, email, info from lidi'
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
                        user = user_cls(
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
            '\nSuccessfully imported %d rows' % counter))
