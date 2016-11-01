
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from fotopruvodce.discussion.forms import Comment as CommentForm
from fotopruvodce.discussion.models import Comment as CommentModel


def comment_list(request):
    object_list = CommentModel.objects.all().order_by('-timestamp')
    context = {
        'object_list': object_list,
    }
    return render(request, 'discussion/list.html', context)


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
