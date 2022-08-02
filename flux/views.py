from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import forms


@login_required
def flux_page(request):

    return render(request, "flux/flux.html")


@login_required
def subscriptions(request):

    if request.method == "POST":
        form = forms.UserFollowsForm(request.POST)
        if form.is_valid():
            user_follows = form.save(commit=False)
            user_follows.user = request.user
            form.save()

    form = forms.UserFollowsForm()
    return render(request, "flux/subscriptions.html", context={"form": form})
