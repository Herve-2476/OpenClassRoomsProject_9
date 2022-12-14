from django.shortcuts import get_object_or_404
from itertools import chain
from django.db.models import BooleanField, F, Q, When, Case, ExpressionWrapper, DateTimeField
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from . import forms, models
from authentication.models import User
import datetime


def annotate_sort_date(query_set):
    return query_set.annotate(
        time_for_sort=ExpressionWrapper(
            Case(When(time_updated=None, then=F("time_created")), default=F("time_updated")),
            output_field=DateTimeField(),
        ),
    )


def sort_and_pagine(request, tickets, reviews):
    tickets = annotate_sort_date(tickets)
    reviews = annotate_sort_date(reviews)
    posts = sorted(chain(tickets, reviews), key=lambda instance: instance.time_for_sort, reverse=True)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return context


@login_required
def subscriptions(request):
    form = forms.UserFollowsForm()
    if request.method == "POST":
        form = forms.UserFollowsForm(request.POST, instance=request.user)
        if form.is_valid():
            new_followed_user = request.POST["username"]
            new_followed_user = get_object_or_404(User, username=new_followed_user)
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
    get_object_or_404(models.UserFollows, id=id_subscription).delete()
    return redirect("subscriptions")


@login_required
def flux_page(request):

    user = request.user
    followed_users = models.UserFollows.objects.filter(user=user)
    followed_users = [user] + [user.followed_user for user in followed_users]

    # we retrieve all the tickets of the user and of the followed users
    # and inside we keep only the tickets without review
    # or with review if the author of the ticket is not the one of the review
    # we mark the ticket if there is or not a rewiew associated (to propose to create a review)
    tickets = models.Ticket.objects.filter(
        Q(user__in=followed_users) & (Q(review__isnull=True) | ~Q(review__user=F("user")))
    ).annotate(
        ticket_with_review=ExpressionWrapper(
            Case(When(Q(review__isnull=False), then=True), default=False),
            output_field=BooleanField(),
        ),
    )

    # we retrieve all the reviews of the user ,of the followed users and of another user if it's your ticket
    reviews = models.Review.objects.filter(Q(user__in=followed_users) | Q(ticket__user=user))

    context = sort_and_pagine(request, tickets, reviews)

    return render(request, "flux/flux.html", context=context)


@login_required
def posts(request):
    user = request.user
    tickets = models.Ticket.objects.filter(user=user)
    reviews = models.Review.objects.filter(user=user)

    context = sort_and_pagine(request, tickets, reviews)
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
    ticket = get_object_or_404(models.Ticket, id=id_ticket)
    old_image = ticket.image
    form = forms.TicketCreateForm(instance=ticket)
    if request.method == "POST":
        form = forms.TicketCreateForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.time_updated = timezone.now()
            ticket.save(old_image=old_image)
            return redirect("posts")
    return render(request, "flux/ticket_modify.html", context={"form": form})


@login_required
def ticket_delete(request, id_ticket):
    instance = get_object_or_404(models.Ticket, id=id_ticket)
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
            review.ticket = get_object_or_404(models.Ticket, id=id_ticket)
            review.save()
            return redirect("flux")
    ticket = get_object_or_404(models.Ticket, id=id_ticket)
    context = {"form": form, "instance": ticket}
    return render(request, "flux/review_create.html", context=context)


@login_required
def review_modify(request, id_review):
    review = get_object_or_404(models.Review, id=id_review)
    form = forms.ReviewCreateForm(instance=review)
    if request.method == "POST":
        form = forms.ReviewCreateForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.time_updated = datetime.datetime.now()
            review.save()
            return redirect("posts")

    return render(request, "flux/review_modify.html", context={"instance": review.ticket, "form": form})


@login_required
def review_delete(request, id_review):
    instance = get_object_or_404(models.Review, id=id_review)
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
