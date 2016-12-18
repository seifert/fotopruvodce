
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from fotopruvodce.photos.forms import Evaluation as EvaluationForm
from fotopruvodce.photos.models import Photo, Comment, Rating


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
    rating = None
    if not request.user.is_anonymous():
        try:
            rating = obj.ratings.get(user=request.user)
        except Rating.DoesNotExist:
            pass

    if request.method == 'POST':
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        form = EvaluationForm(request.POST, logged_user=request.user, photo_user=obj.user)

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

            messages.add_message(request, messages.SUCCESS, 'Úspěšně uloženo')
            return redirect('photos-detail', obj_id)
        else:
            messages.add_message(request, messages.WARNING, 'Opravte chyby ve formuláři')
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

    return render(request, 'photos/account/listing.html', context)


@login_required
def add(request):
    context = {
    }

    return render(request, 'photos/account/add.html', context)


@login_required
def edit(request, photo_id):
    context = {
    }

    return render(request, 'photos/account/edit.html', context)


@login_required
def delete(request, photo_id):
    context = {
    }

    return render(request, 'photos/account/delete.html', context)
