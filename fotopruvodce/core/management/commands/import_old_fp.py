
import hashlib
import os.path
import sys

from datetime import datetime, date, time, timedelta
from functools import lru_cache

import pytz
import requests

from PIL import Image

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from django.core.validators import (
    ValidationError, validate_email, validate_ipv46_address
)
from django.db import connections, transaction
from django.db.models.fields.files import ImageFieldFile
from django.db.utils import IntegrityError
from django.utils.text import slugify

from fotopruvodce.discussion.models import Comment, AnonymousComment
from fotopruvodce.photos.models import (
    Section, Photo, Comment as PhotoComment, Rating as PhotoRating
)
from fotopruvodce.workshops.models import Workshop

User = get_user_model()

EMPTY_IMAGE_NAME = 'noimage.gif'


def date_and_time_to_timestamp(day, hour):
    if day is None:
        day = date(100, 1, 1)
    if hour is None:
        hour = time.min
    try:
        return pytz.timezone(
            "Europe/Prague"
        ).localize(
            datetime.combine(day, hour), is_dst=None
        )
    except pytz.AmbiguousTimeError:
        return pytz.timezone(
            "Europe/Prague"
        ).localize(
            datetime.combine(day, hour) + timedelta(hours=1), is_dst=None
        )


def download_photo(url):
    url_hash = hashlib.md5(bytes(url, 'utf-8')).hexdigest()
    fullpath = os.path.join(settings.MEDIA_ROOT, 'tmp', url_hash)

    if os.path.isfile(fullpath):
        return fullpath
    else:
        if settings.IMPORT_OLD_FP_DO_NOT_DOWNLOAD_PHOTOS:
            return None

    try:
        r = requests.get(url, timeout=5)
    except Exception as e:
        sys.stderr.write("Download '{}' error: {}\n".format(url, str(e)))
        sys.stderr.flush()
        return None
    if r.status_code == 200 and r.headers['content-type'].startswith('image/'):
        with open(fullpath, 'wb') as fd:
            for chunk in r.iter_content(1024 * 1024):
                fd.write(chunk)
        return fullpath
    else:
        return None


def get_image_format(filename):
    try:
        img = Image.open(filename)
    except Exception:
        return None
    else:
        return img.format.lower()


@lru_cache(maxsize=1024)
def get_user(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


@lru_cache(maxsize=1024)
def get_comment(comment_id):
    try:
        return Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return None


@lru_cache(maxsize=32)
def get_photo_section(section_id):
    try:
        return Section.objects.get(id=section_id)
    except Section.DoesNotExist:
        return None


@lru_cache(maxsize=1024)
def get_photo(photo_id):
    try:
        return Photo.objects.get(id=photo_id)
    except Photo.DoesNotExist:
        return None


class Command(BaseCommand):

    help = 'Imports data from old Fotopruvodce database'

    def add_arguments(self, parser):
        pass

    @transaction.atomic
    def handle(self, *args, **options):
        conn_old = connections['old']

        self.handle_users(conn_old)
        self.handle_discussion(conn_old)
        self.handle_photos(conn_old)
        self.handle_workshops(conn_old)

    @transaction.atomic
    def handle_users(self, conn_old):
        self.stdout.write('Import users')

        counter = 0

        # Anonymous user
        anonymous_user = User(
            username='Anonymous', is_active=False,
            is_staff=False, is_superuser=False)
        anonymous_user.save()

        # Import users
        with conn_old.cursor() as cursor_old:
            cursor_old.execute(
                'SELECT id, passwd, jmeno, prijmeni, email, info FROM lidi'
            )
            for row in cursor_old.fetchall():
                username, passwd, jmeno, prijmeni, email, info = row

                displayed_email = email
                try:
                    validate_email(email)
                except ValidationError:
                    email = ''

                try:
                    with transaction.atomic():
                        user = User(
                            username=username, first_name=jmeno,
                            last_name=prijmeni, email=email,
                            is_active=True, is_staff=False,
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

    @transaction.atomic
    def handle_discussion(self, conn_old):
        self.stdout.write('Import discussion')

        anonymous_user = User.objects.get_by_natural_key('Anonymous')
        counter = 0

        with conn_old.cursor() as cursor_old:
            cursor_old.execute(
                'SELECT id, nazev, zprava, tatka, thread, autor, email, '
                'den, cas, ip, registered FROM clanky ORDER BY id'
            )
            for row in cursor_old.fetchall():
                (comment_id, nazev, zprava, tatka, thread, autor,
                 email, den, cas, ip, registered) = row

                # user
                if registered:
                    user = get_user(autor)
                    if not user:
                        self.stdout.write(self.style.ERROR(
                            "Comment {} - convert '{}' to "
                            "anonymous user".format(comment_id, autor)
                        ))
                        user = anonymous_user
                else:
                    user = anonymous_user
                # ip
                if ip:
                    try:
                        validate_ipv46_address(ip)
                    except ValidationError:
                        self.stdout.write(self.style.ERROR(
                            "Comment {} - invalid IP {}".format(comment_id, ip)
                        ))
                        ip = '0.0.0.0'
                else:
                    ip = '0.0.0.0'
                # timestamp
                timestamp = date_and_time_to_timestamp(den, cas)
                # parent
                if tatka != comment_id:
                    parent = get_comment(tatka)
                    if not parent:
                        self.stdout.write(self.style.ERROR(
                            "Comment {} - parent {} doesn't exist, "
                            "try to find thread".format(comment_id, tatka)
                        ))
                        parent = get_comment(thread)
                        if not parent:
                            self.stdout.write(self.style.ERROR(
                                "Comment {} - make orphan".format(comment_id)
                            ))
                            parent = None
                else:
                    parent = None

                comment = Comment(
                    id=comment_id, title=nazev, content=zprava,
                    timestamp=timestamp, ip=ip, user=user, parent=parent)
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

    @transaction.atomic
    def handle_photos(self, conn_old):
        with conn_old.cursor() as cursor_old:
            # Photos sections
            self.stdout.write('Import photos sections')
            counter = 0
            cursor_old.execute(
                'SELECT id, jmeno, popis FROM galerie_temata '
                'WHERE id>1 ORDER BY id'
            )
            for row in cursor_old.fetchall():
                (section_id, jmeno, popis) = row

                section = Section(
                    id=section_id, title=jmeno or '', description=popis or '')
                section.save(force_insert=True)

                counter += 1

            self.stdout.write(self.style.SUCCESS(
                'Successfully imported %d sections' % counter))

            # Photos
            self.stdout.write('Import photos')
            counter = 0
            cursor_old.execute(
                'SELECT id, id_v, den, cas, jmeno, popis, url_nahled, '
                'url_fotky, id_tematu FROM fotogalerie_fotky '
                'ORDER BY id'
            )
            for row in cursor_old.fetchall():
                (photo_id, autor, den, cas, title, description,
                 url_nahled, url_fotky, id_tematu) = row

                photo_src_filename = download_photo(url_fotky)
                thumbnail_src_filename = download_photo(url_nahled)

                title = title or str(photo_id)
                slug_photo = slugify(title)
                description = description or ''
                timestamp = date_and_time_to_timestamp(den, cas)
                user = get_user(autor)
                section = get_photo_section(id_tematu)
                _thumbnail_url = '' if thumbnail_src_filename else url_nahled
                _photo_url = '' if photo_src_filename else url_fotky
                active = not bool(_photo_url or _thumbnail_url)

                photo = Photo(
                    id=photo_id, title=title, description=description,
                    active=active, timestamp=timestamp, user=user,
                    section=section, _photo_url=_photo_url,
                    _thumbnail_url=_thumbnail_url)

                if photo_src_filename:
                    image_format = get_image_format(photo_src_filename)
                    if not image_format:
                        photo.photo = ImageFieldFile(
                            instance=photo,
                            field=Photo.photo.field,
                            name=EMPTY_IMAGE_NAME)
                    else:
                        with open(photo_src_filename, 'rb') as src_fd:
                            photo_src = File(src_fd)
                            photo_dst_filename = "{}-{}.{}".format(
                                user.username,
                                slug_photo,
                                image_format)
                            photo.photo.save(
                                photo_dst_filename, photo_src, save=False)
                else:
                    photo.photo = ImageFieldFile(
                        instance=photo,
                        field=Photo.photo.field,
                        name=EMPTY_IMAGE_NAME)

                if thumbnail_src_filename:
                    image_format = get_image_format(thumbnail_src_filename)
                    if not image_format:
                        photo.thumbnail = ImageFieldFile(
                            instance=photo,
                            field=Photo.thumbnail.field,
                            name=EMPTY_IMAGE_NAME)
                    else:
                        with open(thumbnail_src_filename, 'rb') as src_fd:
                            thumbnail_src = File(src_fd)
                            thumbnail_dst_filename = "{}-{}-thumb.{}".format(
                                user.username,
                                slug_photo,
                                image_format)
                            photo.thumbnail.save(
                                thumbnail_dst_filename, thumbnail_src, save=False)
                else:
                    photo.thumbnail = ImageFieldFile(
                        instance=photo,
                        field=Photo.thumbnail.field,
                        name=EMPTY_IMAGE_NAME)

                photo.save(force_insert=True, force_update=False)

                counter += 1
                if not counter % 1000:
                    self.stdout.write(str(counter))

            self.stdout.write(self.style.SUCCESS(
                'Successfully imported %d photos' % counter))

            # Comments
            self.stdout.write('Import photos comments')
            counter = 0
            errors = 0
            cursor_old.execute(
                'SELECT id_fotky, napsal, den, cas, obsah '
                'FROM fotogalerie_komentare'
            )
            for row in cursor_old.fetchall():
                id_fotky, autor, den, cas, content = row

                content = content or ''
                timestamp = date_and_time_to_timestamp(den, cas)
                photo = get_photo(id_fotky)
                user = get_user(autor)

                if photo:
                    comment = PhotoComment(content=content,
                                           timestamp=timestamp,
                                           photo=photo, user=user)
                    comment.save()
                else:
                    self.stdout.write(self.style.ERROR(
                        "Photo {} doesn't exist".format(id_fotky)
                    ))
                    errors += 1

                counter += 1
                if not counter % 10000:
                    self.stdout.write(str(counter))

            success = counter - errors
            self.stdout.write(self.style.SUCCESS(
                'Successfully imported {} comments, {} errors'.format(
                    success, errors)
            ))

            # Ratings
            self.stdout.write('Import photos ratings')
            counter = 0
            errors = 0
            cursor_old.execute(
                'SELECT kdo, co, kolik, den, cas FROM fotogalerie_body'
            )
            for row in cursor_old.fetchall():
                kdo, co, kolik, den, cas = row

                user = get_user(kdo)
                photo = get_photo(co)
                rating = kolik
                timestamp = date_and_time_to_timestamp(den, cas)

                if photo:
                    rating = PhotoRating(rating=rating, timestamp=timestamp,
                                         photo=photo, user=user)
                    rating.save()
                else:
                    self.stdout.write(self.style.ERROR(
                        "Photo {} doesn't exist".format(co)
                    ))
                    errors += 1

                counter += 1
                if not counter % 10000:
                    self.stdout.write(str(counter))

            success = counter - errors
            self.stdout.write(self.style.SUCCESS(
                'Successfully imported {} ratings, {} errors'.format(
                    success, errors)
            ))

    @transaction.atomic
    def handle_workshops(self, conn_old):
        with conn_old.cursor() as cursor_old:
            self.stdout.write('Import workshops')
            counter = 0
            cursor_old.execute(
                'SELECT id, jmeno, popis, pedagog, den, cas, closed '
                'FROM fotogalerie_workshopy'
            )
            for row_workshop in cursor_old.fetchall():
                (workshop_id, title, description, username,
                 den, cas, closed) = row_workshop

                timestamp = date_and_time_to_timestamp(den, cas)
                user = get_user(username)
                active = not bool(closed)

                workshop = Workshop(
                    id=workshop_id, title=title, description=description,
                    active=active, timestamp=timestamp, instructor=user)
                workshop.save()

                cursor_old.execute(
                    'SELECT id_fotky FROM fotogalerie_workshopy_fotky '
                    'WHERE id_w=%s', (workshop_id,))
                for row_photos in cursor_old.fetchall():
                    photo_id = row_photos[0]
                    photo = get_photo(photo_id)
                    if photo is None:
                        self.stdout.write(self.style.ERROR(
                            "Photo {} doesn't exist".format(photo_id)
                        ))
                    else:
                        workshop.photos.add(photo)

                counter += 1

            self.stdout.write(self.style.SUCCESS(
                'Successfully imported %d rows' % counter))
