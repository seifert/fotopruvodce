
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from fotopruvodce.discussion.forms import Comment as CommentForm
from fotopruvodce.discussion.models import Comment as CommentModel


ACTION_TO_TEMPLATE = {
    'archive': 'discussion/list-archive.html',
    'date': 'discussion/list-date.html',
    'time': 'discussion/list.html',
    'themes': 'discussion/list-themes.html',
    'user': 'discussion/list-user.html',
}


def comment_list(request, action, **kwargs):
    extras = {}
    query = CommentModel.objects.select_related('user').order_by('-timestamp')

    if action == 'archive':
        # TODO:
        query = query.none()
    elif action == 'date':
        filter_date = datetime.strptime(kwargs['date'], "%Y-%m-%d").date()
        query = query.filter(timestamp__date=filter_date)
        extras['filter_date'] = filter_date
    elif action == 'time':
        pass
    elif action == 'themes':
        query = query.filter(parent=None)
    elif action == 'user':
        user = User.objects.get_by_natural_key(kwargs['user'])
        query = query.filter(user=user)
        extras['filter_user'] = user
    else:
        raise Http404

    context = {
        'object_list': query,
    }
    context.update(extras)

    return render(request, ACTION_TO_TEMPLATE[action], context)


@login_required
def comment_add(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            obj = CommentModel(
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content'],
                ip=request.META.get('REMOTE_ADDR', ''),
                user=request.user,
                parent=None
            )
            obj.save()

            messages.add_message(request, messages.SUCCESS, 'Úspěšně přidáno')
            return redirect('comment-list')
    else:
        form = CommentForm()

    context = {
        'form': form,
    }

    return render(request, 'discussion/add.html', context)


def comment_detail(request, obj_id):
    obj = get_object_or_404(CommentModel, id=obj_id)

    if request.method == 'POST':
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        form = CommentForm(request.POST)

        if form.is_valid():
            obj = CommentModel(
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content'],
                ip=request.META.get('REMOTE_ADDR', ''),
                user=request.user,
                parent=obj
            )
            obj.save()

            messages.add_message(request, messages.SUCCESS, 'Úspěšně přidáno')
            return redirect('comment-list')
    else:
        if not obj.title.startswith('Re: '):
            initial = {'title': 'Re: {}'.format(obj.title)}
        else:
            initial = {'title': obj.title}
        form = CommentForm(initial=initial)

    context = {
        'form': form,
        'obj': obj,
    }

    return render(request, 'discussion/detail.html', context)


def comment_thread(request, obj_id):
    obj = get_object_or_404(CommentModel, id=obj_id)

    context = {
        'obj': obj,
    }

    return render(request, 'discussion/thread.html', context)
