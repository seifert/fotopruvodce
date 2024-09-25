import collections
import itertools
import operator
from datetime import datetime
from functools import reduce

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from fotopruvodce.discussion import forms as discussion_forms
from fotopruvodce.discussion.models import Comment

ACTION_TO_TEMPLATE = {
    "archive": "discussion/list-archive.html",
    "date": "discussion/list-date.html",
    "time": "discussion/list.html",
    "themes": "discussion/list-themes.html",
    "user": "discussion/list-user.html",
}


def get_thread_tree(comment):
    """
    Return all related comments for thread identified by *comment* sorted
    by thread's tree.
    """
    comments = (
        Comment.objects.filter(thread=comment.thread)
        .select_related("user", "anonymous")
        .order_by("timestamp")
    )

    parents_map = collections.defaultdict(list)
    for c in comments:
        parents_map[c.parent_id].append(c)

    def build_tree(comment, parents_map, _tree=None):
        if _tree is None:
            _tree = []
        _tree.append(comment)
        for c in parents_map[comment.id]:
            build_tree(c, parents_map, _tree)
        return _tree

    return build_tree(comments[0], parents_map)


def comment_list(request, action, **kwargs):
    context = {}

    query = Comment.objects.select_related("user", "anonymous").order_by("-timestamp")

    if action == "archive":
        if "q" in request.GET:
            form = discussion_forms.Search(request.GET)
            if form.is_valid():
                q = form.cleaned_data["q"]
                query = query.filter(
                    reduce(
                        operator.or_,
                        itertools.chain.from_iterable(
                            (Q(title__icontains=w), Q(content__icontains=w))
                            for w in q.split()
                        ),
                    )
                )
            else:
                q = ""
                query = query.none()
        else:
            q = None
            query = query.none()
            form = discussion_forms.Search()
        context["filter_q"] = q
        context["filter_form"] = form
    elif action == "date":
        filter_date_parts = kwargs["date"].split("-")
        if len(filter_date_parts[0]) == 3:
            filter_date_parts[0] = "0{}".format(filter_date_parts[0])
        filter_date = datetime.strptime("-".join(filter_date_parts), "%Y-%m-%d").date()
        query = query.filter(timestamp__date=filter_date)
        context["filter_date"] = filter_date
    elif action == "time":
        pass
    elif action == "themes":
        query = query.filter(parent=None)
    elif action == "user":
        try:
            user = User.objects.get_by_natural_key(kwargs["user"])
        except User.DoesNotExist:
            user = None
            query = query.filter(anonymous__author=kwargs["user"])
            context["filter_user_anonymous"] = kwargs["user"]
        else:
            query = query.filter(Q(user=user) | Q(anonymous__author=kwargs["user"]))
        context["filter_user"] = user
    else:
        raise Http404

    paginator = Paginator(query, settings.DISCUSSION_OBJECTS_PER_PAGE)
    page = request.GET.get("p", 1)
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)

    context["object_list"] = object_list

    return render(request, ACTION_TO_TEMPLATE[action], context)


@login_required
def comment_add(request):
    if request.method == "POST":
        form = discussion_forms.Comment(request.POST)

        if form.is_valid():
            obj = Comment(
                title=form.cleaned_data["title"],
                content=form.cleaned_data["content"],
                user=request.user,
                parent=None,
            )
            obj.save()

            messages.success(request, "Úspěšně přidáno")
            return redirect("comment-time")
    else:
        form = discussion_forms.Comment()

    context = {
        "form": form,
    }

    return render(request, "discussion/add.html", context)


def comment_detail(request, obj_id):
    obj = get_object_or_404(
        Comment.objects.select_related("user", "anonymous"), id=obj_id
    )

    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        form = discussion_forms.Comment(request.POST)

        if form.is_valid():
            obj = Comment(
                title=form.cleaned_data["title"],
                content=form.cleaned_data["content"],
                user=request.user,
                parent=obj,
            )
            obj.save()

            messages.success(request, "Úspěšně přidáno")
            return redirect("comment-time")
    else:
        if not obj.title.startswith("Re:"):
            initial = {"title": "Re: {}".format(obj.title)}
        else:
            initial = {"title": obj.title}
        form = discussion_forms.Comment(initial=initial)

    context = {
        "form": form,
        "obj": obj,
        "thread_tree": get_thread_tree(obj),
    }

    return render(request, "discussion/detail.html", context)


def comment_thread(request, obj_id):
    obj = get_object_or_404(Comment, id=obj_id)

    context = {
        "obj": obj,
        "thread_tree": get_thread_tree(obj),
    }

    return render(request, "discussion/thread.html", context)
