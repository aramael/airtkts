from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from airtkts.libs.forms import ActionMethodForm, FieldsetsForm


class UserCreationForm(ActionMethodForm, forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    POSSIBLE_ACTIONS = {'_save', '_addanother', '_continue'}

    error_messages = {
        'duplicate_username': "A user with that username already exists.",
        'password_mismatch': "The two password fields didn't match.",
    }
    username = forms.RegexField(label="Columbia UNI", max_length=30,
                                regex=r'^[\w.@+-]+$',
                                help_text="Required. 30 characters or fewer. Letters, digits and "
                                          "@/./+/-/_ only.",
                                error_messages={
                                    'invalid': "This value may contain only letters, numbers and "
                                               "@/./+/-/_ characters."})

    first_name = forms.CharField()
    last_name = forms.CharField()

    password1 = forms.CharField(label="Password",
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation",
                                widget=forms.PasswordInput,
                                help_text="Enter the same password as above, for verification.")

    class Meta:
        model = User
        fields = ('username', )

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):

        data = self.cleaned_data

        user = User.objects.create_user(username=data['username'])

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["username"] + "@columbia.edu"
        user.is_active = True

        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        location_redirect = self.location_redirect(data['action'], user)

        return location_redirect

    def location_redirect(self, action, instance):
        if action == '_save':
            return {"to": 'users_home'}
        elif action == '_addanother':
            return {"to": 'users_new'}
        elif action == '_continue':
            return {"to": 'users_edit', 'user_id': instance.pk}


class UserEditForm(ActionMethodForm, UserChangeForm, FieldsetsForm):

    POSSIBLE_ACTIONS = {'_save', '_addanother', '_continue'}

    fieldsets = (
        (None, {
            'fields': ('username', 'password',)
        }),
        ("Information", {
            'fields': ('first_name', 'last_name', 'email',)
        }),
        ("Permissions", {
            'fields': ('groups', 'user_permissions', 'is_superuser', 'is_active')
        }),
    )

    class Meta(UserChangeForm.Meta):
        exclude = ('last_login', 'date_joined')

    def location_redirect(self, action, instance):
        if action == '_save':
            return {"to": 'users_home'}
        elif action == '_addanother':
            return {"to": 'users_new'}
        elif action == '_continue':
            return {"to": 'users_edit', 'user_id': instance.pk}