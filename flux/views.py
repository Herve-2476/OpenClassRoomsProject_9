from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from . import forms, models
from authentication.models import User


@login_required
def flux_page(request):

    return render(request, "flux/flux.html")


@login_required
def subscriptions(request):
    form = forms.UserFollowsForm()
    if request.method == "POST":

        form = forms.UserFollowsForm(request.POST, instance=request.user)
        if form.is_valid():
            new_followed_user = request.POST["username"]
            new_followed_user = User.objects.get(username=new_followed_user)
            models.UserFollows(user=request.user, followed_user=new_followed_user).save()

    followed_users = models.UserFollows.objects.filter(user=request.user)
    subscripters = models.UserFollows.objects.filter(followed_user=request.user)

    return render(
        request,
        "flux/subscriptions.html",
        context={"form": form, "followed_users": followed_users, "subscripters": subscripters},
    )


@login_required
def subscription_delete(request, id_subscription):
    models.UserFollows.objects.get(id=id_subscription).delete()
    return redirect("subscriptions")
