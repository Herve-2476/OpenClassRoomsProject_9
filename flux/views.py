from itertools import chain
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from . import forms, models
from authentication.models import User


def followed_users(user):
    users = [user.id]
    return users + [user.followed_user for user in models.UserFollows.objects.filter(user=user.id)]


def get_users_viewable_reviews(user):
    users = followed_users(user)
    reviews = []
    for user in users:
        reviews = chain(reviews, models.Review.objects.filter(user=user))
    return reviews


def get_users_viewable_tickets(user):
    users = followed_users(user)
    tickets = []
    for user in users:
        tickets = chain(tickets, models.Ticket.objects.filter(user=user))
    return tickets


@login_required
def flux_page(request):
    reviews = get_users_viewable_reviews(request.user)
    tickets = get_users_viewable_tickets(request.user)

    for obj in chain(reviews, tickets):
        print(obj.user)

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


@login_required
def ticket_create(request):
    form = forms.TicketCreateForm()
    if request.method == "POST":
        form = forms.TicketCreateForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect("flux")

    return render(request, "flux/ticket_create.html", context={"form": form})


@login_required
def ticket_review_create(request):
    form_ticket = forms.TicketCreateForm()
    form_review = forms.ReviewCreateForm()
    if request.method == "POST":
        form_ticket = forms.TicketCreateForm(request.POST, request.FILES)
        form_review = forms.ReviewCreateForm(request.POST)
        if form_ticket.is_valid() and form_review.is_valid():
            ticket = form_ticket.save(commit=False)
            review = form_review.save(commit=False)
            ticket.user = request.user
            review.user = request.user
            ticket.save()
            review.ticket = ticket
            review.save()
            return redirect("flux")

    context = {"form_ticket": form_ticket, "form_review": form_review}
    return render(request, "flux/ticket_review_create.html", context=context)


@login_required
def posts(request):
    user = request.user
    tickets = models.Ticket.objects.filter(user=user)
    reviews = models.Review.objects.filter(user=user)
    posts = sorted(chain(tickets, reviews), key=lambda instance: instance.time_created, reverse=True)
    paginator = Paginator(posts, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return render(request, "flux/posts.html", context=context)
