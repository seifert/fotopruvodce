
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404

from fotopruvodce.photos.models import Photo


def listing(request, action, **kwargs):
    context = {}

    query = Photo.objects.select_related(
        'user', 'section'
    ).filter(
        active=True
    ).order_by(
        '-timestamp'
    )

    paginator = Paginator(query, settings.PHOTOS_OBJECTS_PER_PAGE)
    page = request.GET.get('p', 1)
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)

    context['object_list'] = object_list

    return render(request, 'photos/listing.html', context)


def detail(request, obj_id):
    obj = get_object_or_404(
        Photo.objects.select_related('user', 'section'),
        id=obj_id, active=True
    )

    if request.method == 'GET':
        pass
    else:
        return HttpResponseNotAllowed()

    context = {
        'obj': obj,
    }

    return render(request, 'photos/detail.html', context)
