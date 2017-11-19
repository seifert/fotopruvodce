
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404

from fotopruvodce.workshops.models import Workshop


def listing(request):
    context = {}

    query = Workshop.objects.select_related(
        'instructor',
    ).filter(
        active=True,
    ).order_by(
        '-timestamp'
    )

    paginator = Paginator(query, settings.WORKSHOP_OBJECTS_PER_PAGE)
    page = request.GET.get('p', 1)
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)

    context['object_list'] = object_list

    return render(request, 'workshops/listing.html', context)


def detail(request, obj_id):
    obj = get_object_or_404(
        Workshop.objects.select_related('instructor'),
        id=obj_id, active=True
    )
    obj_photos = obj.photos.select_related(
        'user',
    ).filter(
        deleted=False,
        active=True,
    ).order_by(
        '-timestamp'
    )

    paginator = Paginator(obj_photos, settings.PHOTOS_OBJECTS_PER_PAGE)
    page = request.GET.get('p', 1)
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)

    context = {
        'obj': obj,
        'object_list': object_list,
    }

    return render(request, 'workshops/detail.html', context)
