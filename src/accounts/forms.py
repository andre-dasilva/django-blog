from django import forms
from django.contrib.auth import (
    authenticate, get_user_model, login, logout
)


User = get_user_model()


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("This user does not exists")

            if not user.check_password(password):
                raise forms.ValidationError("Incorrect password")

            if not user.is_active:
                raise forms.ValidationError("This user is no longer active")

        return super(UserLoginForm, self).clean()


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label="Email Address")
    confirm_email = forms.EmailField(label="Confirm Email")
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "confirm_email",
            "password"
        ]

    # Clean methods like clean_...() work on the field.
    # If you don't want to specify the field just use the method clean() (see UserLoginForm)
    def clean_confirm_email(self):
        email = self.cleaned_data.get("email")
        confirm_email = self.cleaned_data.get("confirm_email")

        if email != confirm_email:
            raise forms.ValidationError("Emails must match")

        email_qs = User.objects.filter(email=email)
        if email_qs.exists():
            raise forms.ValidationError("This email has already been registered")

        return confirm_email


