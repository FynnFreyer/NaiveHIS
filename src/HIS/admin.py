from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _

from .models.users import HISUser


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """

    username = forms.CharField(required=False)
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password_control = forms.CharField(label=_('Password confirmation'), widget=forms.PasswordInput)

    title = forms.CharField(required=False)

    class Meta:
        model = HISUser
        fields = '__all__'

    def clean_password_control(self):
        # Check that the two password entries match
        password = self.cleaned_data.get('password')
        password_control = self.cleaned_data.get('password_control')

        if password and password_control and password != password_control:
            raise ValidationError(_("Passwords don't match"))

        return password_control

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username and not self.Meta.model.objects.is_valid_username(username):
            raise ValidationError(_('Invalid username'))

        return username

    def save(self, commit=True):
        user = super().save(commit=False)

        user = self.Meta.model.objects.create_user(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            title=self.cleaned_data['title'],
            password=self.cleaned_data['password_control'],
            commit=commit
        )

        return user


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admins
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = HISUser
        fields = '__all__'


class HISUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        'username',
        'email',
        'title',
        'first_name',
        'last_name',
        'is_staff',
        'is_admin',
        'is_active'
    )

    list_filter = (
        'is_admin',
        'is_staff',
        'is_active'
    )

    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                ('email', 'username'),
                ('password',)
            )
        }),
        (_('Personal info'), {
            'classes': ('wide',),
            'fields': (
                'title',
                ('first_name', 'last_name')
            )
        }),
        (_('Status'), {
            'classes': ('collapse',),
            'fields': (
                ('is_staff', 'is_active', 'is_admin'),
            )
        }),
    )

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                ('password', 'password_control')
            )
        }),
        (_('Personal info'), {
            'classes': ('wide',),
            'fields': (
                'title',
                ('first_name', 'last_name')
            )
        }),
        (_('Status'), {
            'classes': ('collapse',),
            'fields': (
                'username',
                ('is_staff', 'is_active', 'is_admin'),
            )
        }),
    )

    search_fields = ('email', 'username', 'last_name')
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(HISUser, HISUserAdmin)
