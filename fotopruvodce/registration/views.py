
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect

from fotopruvodce.registration.crypt import encode_ts, decode_ts
from fotopruvodce.registration.forms import Register


def registration(request):
    ts = time.time()
    ts_encrypted = encode_ts(ts)

    if request.method == 'POST':
        form = Register(request.POST.copy())

        if form.is_valid():
            ts_form = decode_ts(form.cleaned_data['ts'])
            if (
                form.cleaned_data['url'] or
                ts_form is None or
                (ts - ts_form) < settings.ANTIBOT_MIN_TIME
            ):
                messages.add_message(
                    request, messages.WARNING,
                    'Účet nebyl založen z důvodu podezření na spam')
                return redirect('homepage')

            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                )
            except IntegrityError:
                form.add_error('username', 'Uživatel již existuje')
            else:
                login(
                    request, user,
                    backend='django.contrib.auth.backends.ModelBackend')

                messages.add_message(
                    request, messages.SUCCESS, 'Účet byl úspěšně založen')
                return redirect('homepage')

            form.cleaned_data['ts'] = ts_encrypted
        else:
            form.data['ts'] = ts_encrypted
    else:
        form = Register(initial={'ts': ts_encrypted})

    context = {
        'form': form,
    }

    return render(request, 'registration/register.html', context)
