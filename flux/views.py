from itertools import chain
from django.db.models import Case, Value, When, CharField, BooleanField
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from . import forms, models
from authentication.models import User


@login_required
def subscriptions(request):
    form = forms.UserFollowsForm()
    if request.method == "POST":

        form = forms.UserFollowsForm(request.POST, instance=request.user)
        if form.is_valid():
            new_followed_user = request.POST["username"]
            new_followed_user = User.objects.get(username=new_followed_user)
            models.UserFollows(user=request.user, followed_user=new_followed_user).save()
            form = forms.UserFollowsForm()

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
def flux_page(request):

    user = request.user
    followed_users = models.UserFollows.objects.filter(user=user)
    followed_users = [user] + [user.followed_user for user in followed_users]
    # we retrieve all the tickets of the user and of the followed users
    tickets = models.Ticket.objects.filter(user__in=followed_users).annotate(
        ticket_with_review=Value(False, BooleanField())
    )

    # we keep only the tickets without review or with review if the author of the ticket is not the one of the review
    tickets = [
        ticket
        for ticket in tickets
        if ticket.review_set.all().count() == 0
        or (ticket.review_set.all().count() == 1 and ticket.user != ticket.review_set.all()[0].user)
    ]

    # we mark the ticket if there is or not a rewiew associated
    for ticket in tickets:
        if ticket.review_set.all().count() == 1:
            ticket.ticket_with_review = True
            ticket.save(image_resize=False)
    # we retrieve all the tickets of the user and of the followed users
    reviews = models.Review.objects.all()
    reviews = [review for review in reviews if review.user in followed_users or (review.ticket.user == user)]

    posts = sorted(chain(tickets, reviews), key=lambda instance: instance.time_created, reverse=True)

    paginator = Paginator(posts, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}

    return render(request, "flux/flux.html", context=context)


@login_required
def posts(request):
    user = request.user
    tickets = models.Ticket.objects.filter(user=user)
    if False:
        # we keep only the tickets without review or if the user is author of both the ticket and the review
        tickets = [
            ticket
            for ticket in tickets
            if ticket.review_set.all().count() == 0 or user == ticket.review_set.all()[0].user
        ]
    reviews = models.Review.objects.filter(user=user)
    posts = sorted(chain(tickets, reviews), key=lambda instance: instance.time_created, reverse=True)
    paginator = Paginator(posts, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return render(request, "flux/posts.html", context=context)


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
def ticket_modify(request, id_ticket):
    ticket = models.Ticket.objects.get(id=id_ticket)
    form = forms.TicketCreateForm(instance=ticket)
    if request.method == "POST":
        form = forms.TicketCreateForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect("posts")

    return render(request, "flux/ticket_modify.html", context={"form": form})


@login_required
def ticket_delete(request, id_ticket):
    instance = models.Ticket.objects.get(id=id_ticket)
    old_image = instance.image

    if request.method == "POST":
        instance.delete(old_image=old_image)
        return redirect("posts")
    return render(request, "flux/ticket_delete.html", {"instance": instance})


@login_required
def review_create(request, id_ticket):
    form = forms.ReviewCreateForm()
    if request.method == "POST":
        form = forms.ReviewCreateForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ticket = models.Ticket.objects.get(id=id_ticket)
            review.save()
            return redirect("flux")
    ticket = models.Ticket.objects.get(id=id_ticket)
    context = {"form": form, "ticket": ticket}
    return render(request, "flux/review_create.html", context=context)


@login_required
def review_modify(request, id_review):
    review = models.Review.objects.get(id=id_review)
    form = forms.ReviewCreateForm(instance=review)
    if request.method == "POST":
        form = forms.ReviewCreateForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect("posts")

    return render(request, "flux/review_modify.html", context={"form": form})


@login_required
def review_delete(request, id_review):
    instance = models.Review.objects.get(id=id_review)
    if request.method == "POST":
        instance.delete()
        return redirect("posts")
    return render(request, "flux/review_delete.html", {"instance": instance})


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
