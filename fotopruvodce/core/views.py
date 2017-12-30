
import json

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import response
from django.shortcuts import render, redirect

from fotopruvodce.core.forms import UserEdit, UserSetPassword
from fotopruvodce.core.logging import logger
from fotopruvodce.core.models import Preferences


def homepage(request):
    if request.user.is_anonymous:
        preferences = Preferences()
    else:
        preferences = request.user.profile.preferences

    context = {
        'preferences': preferences,
    }

    return render(request, 'core/homepage.html', context)


@login_required
def set_preference(request):
    if request.method != 'POST':
        return response.HttpResponseNotAllowed(['POST'])

    name = request.POST.get('name')
    if name and hasattr(request.user.profile.preferences, name):
        try:
            value = json.loads(request.POST['value'])
            setattr(request.user.profile.preferences, name, value)
        except Exception:
            logger.exception("set_preference: invalid value %r",
                             request.POST.get('value'))
            return response.HttpResponseBadRequest()
        request.user.profile.save()
        return response.HttpResponse('OK')

    logger.warning("set_preference: invalid preference %r", name)
    return response.HttpResponseBadRequest()


@login_required
def user_home(request):
    form_user_edit = None
    form_set_password = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'user-edit':
            form_user_edit = UserEdit(request.POST)
            if form_user_edit.is_valid():
                request.user.first_name = form_user_edit.cleaned_data['first_name']
                request.user.last_name = form_user_edit.cleaned_data['last_name']
                request.user.email = form_user_edit.cleaned_data['email']
                request.user.save()
                request.user.profile.description = form_user_edit.cleaned_data['description']
                request.user.profile.displayed_email = form_user_edit.cleaned_data['displayed_email']
                request.user.profile.save()

                messages.success(request, 'Údaje byly uloženy')
                return redirect('account-personal-info')
        elif action == 'set-password':
            form_set_password = UserSetPassword(request.POST, user=request.user)
            if form_set_password.is_valid():
                request.user.set_password(form_set_password.cleaned_data['new1'])
                request.user.save()

                login(request, request.user)

                messages.success(request, 'Heslo bylo změněno')
                return redirect('account-personal-info')
        else:
            messages.error(request, 'Neznámá akce')

    if form_user_edit is None:
        form_user_edit = UserEdit(
            initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'description': request.user.profile.description,
                'displayed_email': request.user.profile.displayed_email,
            }
        )
    if form_set_password is None:
        form_set_password = UserSetPassword(user=request.user)

    context = {
        'form_user_edit': form_user_edit,
        'form_set_password': form_set_password,
    }

    return render(request, 'core/account-personal-info.html', context)
