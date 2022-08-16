from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username",)


class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Nom d'utilisateur"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Mot de passe"}))
