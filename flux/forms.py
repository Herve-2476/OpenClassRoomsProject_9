from django import forms
from django.core.exceptions import ValidationError
from . import models


class UserFollowsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get("instance", None)
        super().__init__(*args)

    username = forms.CharField(label="Utilisateur à suivre", max_length=150)

    def clean_username(self):
        new_followed_user = self.cleaned_data["username"]
        connected_user = self.instance.username
        followed_users = models.UserFollows.objects.filter(user=self.instance)
        if new_followed_user == connected_user:
            raise ValidationError("Vous ne pouvez pas vous suivre...")

        elif new_followed_user in [str(user.followed_user) for user in followed_users]:
            raise ValidationError(f"Vous suivez déjà l'utilisateur {new_followed_user}")

        elif new_followed_user not in [user.username for user in models.User.objects.all()]:
            raise ValidationError((f"L'utilisateur {new_followed_user} n'existe pas"))


class UnsubscribeForm(forms.ModelForm):
    unsubscribe_tag = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = models.UserFollows
        fields = []
