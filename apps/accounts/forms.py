from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Form for updating user profile details"""

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        # Check if username is already taken by another user
        if (
            username
            and User.objects.filter(username=username)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("This username is already taken")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        # Check if email is already taken by another user
        if (
            email
            and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists()
        ):
            raise forms.ValidationError("This email is already in use")
        return email


class UserAdminForm(forms.ModelForm):
    """Form for admins to manage user auth records"""

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select roles for this user.",
    )

    def __init__(self, *args, **kwargs):
        from rolepermissions.checkers import has_role

        self.user = kwargs.pop("user", None)
        super(UserAdminForm, self).__init__(*args, **kwargs)

        is_superuser = self.user and self.user.is_superuser
        is_super_admin = self.user and has_role(self.user, "super_admin")

        if not (is_superuser or is_super_admin):
            if "groups" in self.fields:
                del self.fields["groups"]

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active", "groups"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "app-input"}),
            "email": forms.EmailInput(attrs={"class": "app-input"}),
            "first_name": forms.TextInput(attrs={"class": "app-input"}),
            "last_name": forms.TextInput(attrs={"class": "app-input"}),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "app-btn p-2 text-primary border-border rounded focus:ring-primary"
                }
            ),
        }

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "app-input"}),
        help_text="Leave blank to keep current password.",
        label="Password",
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "app-input"}),
        help_text="Enter the same password as above, for verification.",
        label="Confirm Password",
    )

    def clean_confirm_password(self):
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("confirm_password")
        if p1 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        if p2 and not p1:
            raise forms.ValidationError("Please enter a new password.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        if commit:
            user.save()
            self.save_m2m()

        return user

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if (
            username
            and User.objects.filter(username=username)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("This username is already taken")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if (
            email
            and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists()
        ):
            raise forms.ValidationError("This email is already in use")
        return email
