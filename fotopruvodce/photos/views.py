
from calendar import monthrange
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Avg, Count, Sum
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from fotopruvodce.photos.forms import (
    Edit as PhotoEditForm, Add as PhotoAddForm, Evaluation as EvaluationForm)
from fotopruvodce.photos.models import Section, Photo, Comment, Rating


ACTION_TO_TEMPLATE = {
    'date': 'photos/listing-date.html',
    'month': 'photos/listing-month.html',
    'time': 'photos/listing.html',
    'section': 'photos/listing-section.html',
    'user': 'photos/listing-user.html',
}


def dt_to_datetime(dt: str, fmt: str='%Y-%m-%d') -> datetime:
    parts = dt.split('-')
    if len(parts[0]) == 3:
        parts[0] = "0{}".format(parts[0])
    return datetime.strptime('-'.join(parts), fmt)


def listing(request, action, **kwargs):
    context = {}

    query = Photo.objects.select_related(
        'user', 'section'
    ).filter(
        deleted=False,
        active=True,
    ).order_by(
        '-timestamp'
    )

    if action == 'date':
        filter_date = dt_to_datetime(kwargs['date']).date()
        query = query.filter(timestamp__date=filter_date)
        context['filter_date'] = filter_date
    elif action == 'month':
        filter_dt = dt_to_datetime(kwargs['month'], '%Y-%m')
        filter_dt_stop = filter_dt.replace(
            day=monthrange(filter_dt.year, filter_dt.month)[1],
            hour=23, minute=59, second=59, microsecond=999999)
        query = query.filter(timestamp__range=(filter_dt, filter_dt_stop))
        context['filter_date'] = filter_dt
    elif action == 'time':
        pass
    elif action == 'section':
        if kwargs['section']:
            section = get_object_or_404(Section, id=int(kwargs['section']))
            query = query.filter(section_id=section)
        else:
            section = None
            query = query.filter(section=None)
        context['filter_section'] = section
    elif action == 'user':
        user = get_object_or_404(User, username=kwargs['user'])
        query = query.filter(user=user)
        context['filter_user'] = user
    else:
        raise Http404

    paginator = Paginator(query, settings.PHOTOS_OBJECTS_PER_PAGE)
    page = request.GET.get('p', 1)
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)

    context['object_list'] = object_list

    return render(request, ACTION_TO_TEMPLATE[action], context)


def total_score_listing(request):
    context = {}

    query = Rating.objects.values(
        'photo_id', 'photo__title', 'photo__timestamp',
        'photo__thumbnail', 'photo__user__username'
    ).filter(
        photo__deleted=False, photo__active=True
    ).annotate(
        Avg('rating'), Count('rating'), Sum('rating')
    ).order_by(
        '-rating__sum'
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

    return render(request, 'photos/listing-score.html', context)


def comments_listing(request):
    context = {}

    query = Comment.objects.select_related(
        'photo', 'photo__user', 'user'
    ).filter(
        photo__deleted=False, photo__active=True
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

    return render(request, 'photos/listing-comments.html', context)


def themes(request):
    sections = Section.objects.order_by('title')
    context = {
        'object_list': sections
    }
    return render(request, 'photos/sections.html', context)


def detail(request, obj_id):
    obj = get_object_or_404(
        Photo.objects.select_related('user', 'section'),
        id=obj_id, deleted=False, active=True
    )
    form = None
    rating = None
    if not request.user.is_anonymous():
        try:
            rating = obj.ratings.get(user=request.user)
        except Rating.DoesNotExist:
            pass

    if request.method == 'POST':
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        form = EvaluationForm(
            request.POST, logged_user=request.user,
            photo=obj, logged_user_rating=rating)

        if form.is_valid():
            if form.cleaned_data['content']:
                comment = Comment(
                    content=form.cleaned_data['content'],
                    photo=obj, user=request.user)
                comment.save(force_insert=True, force_update=False)

            if form.cleaned_data['rating'] is not None:
                if rating is not None:
                    rating.rating = form.cleaned_data['rating']
                    rating.save(force_insert=False, force_update=True)
                else:
                    rating = Rating(
                        rating=form.cleaned_data['rating'],
                        photo=obj, user=request.user)
                    rating.save(force_insert=True, force_update=False)
            else:
                if rating is not None:
                    rating.delete()

            messages.add_message(
                request, messages.SUCCESS, 'Úspěšně uloženo')
            return redirect('photos-detail', obj_id)
        else:
            messages.add_message(
                request, messages.WARNING, 'Opravte chyby ve formuláři')
    else:
        initial = {}
        if rating is not None:
            initial['rating'] = rating.rating
        form = EvaluationForm(initial=initial)

    context = {
        'form': form,
        'obj': obj,
    }

    return render(request, 'photos/detail.html', context)


@login_required
def listing_account(request):
    context = {}

    query = Photo.objects.select_related(
        'section'
    ).filter(
        user=request.user,
        deleted=False,
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

    return render(request, 'photos/account/listing.html', context)


@login_required
def add(request):
    back = request.GET.get('back')

    if request.method == 'POST':
        form = PhotoAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Úspěšně uloženo')
            if back:
                return redirect(back)
            else:
                return redirect('account-photos-listing')
    else:
        form = PhotoAddForm()

    context = {
        'form': form,
        'back': back,
    }

    return render(request, 'photos/account/add.html', context)


@login_required
def edit(request, photo_id):
    obj = get_object_or_404(
        Photo, id=photo_id, user=request.user, deleted=False
    )
    if obj._thumbnail_url or obj._photo_url:
        form_cls = PhotoAddForm
    else:
        form_cls = PhotoEditForm
    back = request.GET.get('back')

    if request.method == 'POST':
        form = form_cls(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Úspěšně uloženo')
            if back:
                return redirect(back)
            else:
                return redirect('account-photos-listing')
    else:
        form = form_cls(instance=obj)

    context = {
        'form': form,
        'back': back,
    }

    return render(request, 'photos/account/edit.html', context)


@login_required
def delete(request, photo_id):
    obj = get_object_or_404(
        Photo, id=photo_id, user=request.user, deleted=False
    )
    back = request.GET.get('back')

    if request.method == 'POST':
        obj.deleted = True
        obj.save()
        messages.add_message(request, messages.SUCCESS, 'Úspěšně smazáno')
        if back:
            return redirect(back)
        else:
            return redirect('account-photos-listing')

    context = {
        'obj': obj,
        'back': back,
    }

    return render(request, 'photos/account/delete.html', context)
