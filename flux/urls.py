from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views


urlpatterns = [
    path("flux/", views.flux_page, name="flux"),
    path("flux/subscriptions/", views.subscriptions, name="subscriptions"),
    path("flux/subscriptions/delete/<int:id_subscription>/", views.subscription_delete, name="subscription_delete"),
    path("flux/ticket/create/", views.ticket_create, name="ticket_create"),
    path("flux/ticket_review/create/", views.ticket_review_create, name="ticket_review_create"),
    path("flux/posts/", views.posts, name="posts"),
]
