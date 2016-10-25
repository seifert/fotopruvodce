
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from fotopruvodce.registration.forms import Register


def registration(request):
    if request.method == 'POST':
        form = Register(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            login(request, user)
            return redirect("homepage")
    else:
        form = Register()

    context = {
        'form': form,
    }

    return render(request, 'registration/register.html', context)
