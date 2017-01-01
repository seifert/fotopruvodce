
from urllib.parse import urlencode

from django.conf import settings
from django.http.response import (
    HttpResponseNotFound, HttpResponseRedirect, HttpResponsePermanentRedirect
)
from django.urls import reverse
from django.utils import timezone

if settings.DEBUG:
    HttpResponsePermanentRedirect = HttpResponseRedirect


class OldFotopruvodceRedir(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if isinstance(response, HttpResponseNotFound):
            path = request.path

            if path == '/index.php':
                response = self.homepage(request, response)
            elif path == '/fotoforum.phtml':
                response = self.fotoforum(request, response)
            elif path == '/clanek.phtml':
                response = self.fotoforum_clanek(request, response)
            elif path == '/archiv.phtml':
                response = self.fotoforum_archiv(request, response)
            elif path == '/fotogalerie/fotogalerie.phtml':
                response = self.fotogalerie(request, response)
            elif path == '/fotogalerie/fotka.phtml':
                response = self.fotogalerie_fotka(request, response)
            elif path == '/fotogalerie/fotky.phtml':
                response = self.fotogalerie_fotky(request, response)
            elif path == '/fotogalerie/autori.phtml':
                response = self.fotogalerie_autori(request, response)
            elif path == '/fotogalerie/komentare.phtml':
                response = self.fotogalerie_komentare(request, response)
            elif path == '/fotogalerie/temata.phtml':
                response = self.fotogalerie_temata(request, response)
            elif path == '/fotogalerie/mesice.phtml':
                response = self.fotogalerie_mesice(request, response)
            elif path == '/fotogalerie/distribuce.phtml':
                response = self.fotogalerie_distribuce(request, response)

        return response

    def homepage(self, request, response):
        return HttpResponsePermanentRedirect(
            reverse('homepage'))

    def fotoforum(self, request, response):
        naction = request.GET.get('NACTION')
        if not naction or naction == 'clanky':
            path = reverse('comment-time')
            response = HttpResponsePermanentRedirect(path)
        elif naction == 'temata':
            path = reverse('comment-themes')
            response = HttpResponsePermanentRedirect(path)
        elif naction == 'den':
            day = request.GET.get('den')
            if not day:
                day = timezone.now().strftime('%Y-%m-%d')
            path = reverse('comment-date',  kwargs={'date': day})
            response = HttpResponsePermanentRedirect(path)
        elif naction == 'author':
            username = request.GET.get('author')
            if username:
                path = reverse('comment-user', kwargs={'user': username})
                response = HttpResponsePermanentRedirect(path)
        return response

    def fotoforum_clanek(self, request, response):
        comment_id = request.GET.get('clanek')
        if comment_id:
            naction = request.GET.get('NACTION')
            if naction is None:
                path = reverse('comment-detail', args=(comment_id,))
                response = HttpResponsePermanentRedirect(path)
            elif naction == 'thread':
                path = reverse('comment-thread', args=(comment_id,))
                response = HttpResponsePermanentRedirect(path)
        return response

    def fotoforum_archiv(self, request, response):
        q = request.GET.get('hledej')
        if request.GET.get('NACTION') == 'find' and q:
            path = reverse('comment-archive', kwargs={'action': 'archive'})
            qs = urlencode({'q': q}, doseq=True)
            response = HttpResponsePermanentRedirect('{}?{}'.format(path, qs))
        return response

    def fotogalerie(self, request, response):
        return HttpResponsePermanentRedirect(reverse('photos-listing-time'))

    def fotogalerie_fotka(self, request, response):
        photo_id = request.GET.get('fotka')
        if photo_id:
            path = reverse('photos-detail', args=(photo_id,))
            response = HttpResponsePermanentRedirect(path)
        return response

    def fotogalerie_fotky(self, request, response):
        month = request.GET.get('mesic')
        section = request.GET.get('tema')
        if not month and not section:
            path = reverse('photos-listing-time')
            response = HttpResponsePermanentRedirect(path)
        elif month and not section:
            path = reverse('photos-listing-month', kwargs={'month': month})
            response = HttpResponsePermanentRedirect(path)
        elif not month and section:
            if section == '1':
                path = reverse('photos-listing-no-section')
            else:
                path = reverse(
                    'photos-listing-section', kwargs={'section': section})
            response = HttpResponsePermanentRedirect(path)
        return response

    def fotogalerie_autori(self, request, response):
        username = request.GET.get('autor')
        if username:
            path = reverse('photos-listing-user', kwargs={'user': username})
            response = HttpResponsePermanentRedirect(path)
        return response

    def fotogalerie_komentare(self, request, response):
        username = request.GET.get('autor')
        if username:
            path = reverse(
                'photos-listing-comments-user', kwargs={'user': username})
        else:
            path = reverse('photos-listing-comments')
        return HttpResponsePermanentRedirect(path)

    def fotogalerie_temata(self, request, response):
        return HttpResponsePermanentRedirect(reverse('photos-sections'))

    def fotogalerie_mesice(self, request, response):
        return HttpResponsePermanentRedirect(reverse('photos-months'))

    def fotogalerie_distribuce(self, request, response):
        return HttpResponsePermanentRedirect(reverse('photos-listing-score'))
