
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect

from fotopruvodce.registration.forms import Register


def registration(request):
    if request.method == 'POST':
        form = Register(request.POST)

        if form.is_valid():
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                )
            except IntegrityError:
                form.add_error('username', 'Uživatel již existuje')
            else:
                login(request, user)

                messages.add_message(request, messages.SUCCESS, 'Účet byl úspěšně založen')
                return redirect('homepage')
    else:
        form = Register()

    context = {
        'form': form,
    }

    return render(request, 'registration/register.html', context)
