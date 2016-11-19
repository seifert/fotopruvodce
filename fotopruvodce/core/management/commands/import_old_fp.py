
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
from django.db.utils import IntegrityError
from django.utils.text import slugify

from fotopruvodce.discussion.models import Comment, AnonymousComment
from fotopruvodce.photos.models import (
    Section, Photo, Comment as PhotoComment, Rating as PhotoRating
)

User = get_user_model()

EMPTY_PHOTO_PATH = os.path.join(os.path.dirname(__file__), 'noimage.gif')
EMPTY_THUMBNAIL_PATH = EMPTY_PHOTO_PATH


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
                    comment_id=comment_id, title=nazev, content=zprava,
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
                'SELECT id, jmeno, popis FROM galerie_temata ORDER BY id'
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

                title = title or str(photo_id)
                slug = slugify(title)
                slug_photo = slug[:50]
                description = description or ''
                timestamp = date_and_time_to_timestamp(den, cas)
                user = get_user(autor)
                section = get_photo_section(id_tematu)
                photo_src_filename = download_photo(url_fotky)
                if photo_src_filename:
                    _photo_url = ''
                else:
                    photo_src_filename = EMPTY_PHOTO_PATH
                    _photo_url = url_fotky
                thumbnail_src_filename = download_photo(url_nahled)
                if thumbnail_src_filename:
                    _thumbnail_url = ''
                else:
                    thumbnail_src_filename = EMPTY_THUMBNAIL_PATH
                    _thumbnail_url = url_nahled
                active = not bool(_photo_url or _thumbnail_url)

                with open(photo_src_filename, 'rb') as photo_src_fd,\
                        open(thumbnail_src_filename, 'rb') as thumbnail_src_fd:
                    photo_src = File(photo_src_fd)
                    thumbnail_src = File(thumbnail_src_fd)

                    photo_dst_filename = "{}-{}.{}".format(
                        photo_id,
                        slug_photo,
                        get_image_format(photo_src_filename))
                    thumbnail_dst_filename = "{}-{}-thumb.{}".format(
                        photo_id,
                        slug_photo,
                        get_image_format(thumbnail_src_filename))

                    photo = Photo(
                        id=photo_id, title=title, description=description,
                        active=active, timestamp=timestamp, user=user,
                        section=section, _photo_url=_photo_url,
                        _thumbnail_url=_thumbnail_url)
                    photo.photo.save(
                        photo_dst_filename, photo_src, save=False)
                    photo.thumbnail.save(
                        thumbnail_dst_filename, thumbnail_src, save=False)
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
