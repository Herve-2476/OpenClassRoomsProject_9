from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms

from flux.models import UserFollows


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username",)


class FollowUsersForm(forms.ModelForm):
    class Meta:
        model = UserFollows
        fields = ["followed_user"]
