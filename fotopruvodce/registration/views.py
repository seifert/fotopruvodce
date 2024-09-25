from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import redirect, render

from fotopruvodce.registration.crypt import ReversedTimestampSigner, SignatureTooFresh
from fotopruvodce.registration.forms import Register


def registration(request):
    signer = ReversedTimestampSigner()

    if request.method == "POST":
        form = Register(request.POST.copy())

        if form.is_valid():
            try:
                signer.unsign(
                    form.cleaned_data["signature"], min_age=settings.ANTIBOT_MIN_TIME
                )
                antibot_pass = True
            except (KeyError, SignatureTooFresh):
                antibot_pass = False
            if form.cleaned_data["url"] or not antibot_pass:
                messages.error(request, "Účet nebyl založen z důvodu podezření na spam")
                return redirect("homepage")

            try:
                user = User.objects.create_user(
                    username=form.cleaned_data["username"],
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password1"],
                )
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                messages.success(request, "Účet byl úspěšně založen")
                return redirect("homepage")
            except IntegrityError:
                form.add_error("username", "Uživatel již existuje")

            form.cleaned_data["signature"] = signer.sign("fotopruvodce")
        else:
            form.data["signature"] = signer.sign("fotopruvodce")
    else:
        form = Register(initial={"signature": signer.sign("fotopruvodce")})

    context = {
        "form": form,
    }

    return render(request, "registration/register.html", context)
