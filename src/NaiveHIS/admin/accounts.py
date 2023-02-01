from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password

from django.utils.translation import gettext_lazy as _

from ..models.common import AddressRequiredMixin, PersonMixin
from .common import (
    ADDRESS_FIELDSETS,
    ADDRESS_LIST_DISPLAY,
    # ADDRESS_LIST_FILTER,
    ADDRESS_SEARCH_FIELDS,
    ADDRESS_ORDERING,
    PERSON_FIELDSETS,
    PERSON_LIST_DISPLAY,
    # PERSON_LIST_FILTER,
    PERSON_SEARCH_FIELDS,
    PERSON_ORDERING, BlankableAdminMixin
)

from ..models.accounts import (
    HISAccount,
    Employee,
    AdministrativeEmployee,
    Doctor, DoctorQualification,
    Nurse,
    GeneralPersonnel
)

from ..models.objects import Department

_UNAME_MAX_LEN = HISAccount._meta.get_field('username').max_length


class BaseAccountCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=_UNAME_MAX_LEN, label=_('Nutzername'))
    email = forms.EmailField(widget=forms.EmailInput, label=_('E-Mail-Adresse'), required=False)
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password_control = forms.CharField(label=_('Password confirmation'), widget=forms.PasswordInput)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password_control'])

        if commit:
            user.save()

        return user

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if (not HISAccount.objects.is_valid_username(username) and not self.instance.username == username
                or (self.fields['username'].required and not username)):
            raise ValidationError(_('Ungültiger Nutzername'))

        if not username:
            # TODO if username not required, assert first_name, last_name
            first_name = self.cleaned_data['first_name']
            last_name = self.cleaned_data['last_name']

            username = HISAccount.objects.get_valid_username(first_name, last_name)

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = None if email == '' else email

        if email is not None:
            validate_email(email)

        return email

    def _compare_password_with_control(self, pw_fieldname: str):
        # Check that the two password entries match
        password = self.cleaned_data.get(pw_fieldname)
        password_control = self.cleaned_data.get('password_control')

        if password != password_control:
            raise ValidationError(_("Passwörter stimmen nicht überein"))

        return password_control

    def clean_password_control(self):
        password = self._compare_password_with_control('password')

        # TODO activate
        # User creation always needs validation
        # validate_password(password)

        return password


class BaseAccountChangeForm(BaseAccountCreationForm):
    password = ReadOnlyPasswordHashField(required=False, label=_('Password'))
    new_password = forms.CharField(required=False, label=_('Change password'), widget=forms.PasswordInput)
    password_control = forms.CharField(required=False, label=_('Password confirmation'), widget=forms.PasswordInput)

    def save(self, instance=None, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data['password_control']
        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user

    def clean_password_control(self):
        password_control = self._compare_password_with_control('new_password')

        # TODO activate
        # User change only needs validation if passwords are set
        # if password_control:
        #     validate_password(password_control)

        return password_control


class HISAccountChangeForm(BaseAccountChangeForm):
    email = forms.EmailField(widget=forms.EmailInput, required=False)

    class Meta:
        model = HISAccount
        fields = '__all__'


class HISAccountCreationForm(BaseAccountCreationForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput, label=_('E-Mail-Adresse'))

    class Meta:
        model = HISAccount
        fields = '__all__'


ACCOUNT_FIELDSETS = (
    (_('Account Informationen'), {
        'classes': ('wide',),
        'fields': (
            ('username', 'email'),
            ('password',),
            ('new_password', 'password_control'),
        )
    }),
    (_('Status'), {
        'classes': ('collapse', 'wide'),
        'fields': (
            ('is_staff', 'is_active', 'is_admin'),
            ('user_permissions',),
            ('groups',)
        )
    }),
)

ACCOUNT_ADD_FIELDSETS = (
    (_('Account Informationen'), {
        'classes': ('wide',),
        'fields': (
            ('username', 'email'),
            ('password', 'password_control')
        )
    }),
    (_('Status'), {
        'classes': ('collapse', 'wide'),
        'fields': (
            ('is_staff', 'is_active', 'is_admin'),
            ('user_permissions',),
            ('groups',)
        )
    }),
)

ACCOUNT_LIST_DISPLAY = (
    'username',
    'email',
    'is_active',
)

ACCOUNT_LIST_FILTER = (
    'is_admin',
    'is_staff',
    'is_active',
)


class HISAccountAdmin(UserAdmin):
    # The forms to add and change user instances
    form = HISAccountChangeForm
    add_form = HISAccountCreationForm

    list_display = ACCOUNT_LIST_DISPLAY

    list_filter = ACCOUNT_LIST_FILTER

    search_fields = ('email', 'username')
    ordering = ('username',)
    filter_horizontal = ()

    fieldsets = ACCOUNT_FIELDSETS

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = ACCOUNT_ADD_FIELDSETS


class EmployeeChangeForm(BaseAccountChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields['email'].required = True

    class Meta:
        model = Employee
        fields = '__all__'


# TODO duplication
class EmployeeCreationForm(BaseAccountCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields['email'].required = True

    class Meta:
        model = Employee
        fields = '__all__'


ORG_FIELDSETS = (_('Organisationseinheit'), {
    'classes': ('wide',),
    'fields': (
        ('department',),
        ('rank',),
    )
}),


class EmployeeAdmin(HISAccountAdmin, BlankableAdminMixin):
    form = EmployeeChangeForm
    add_form = EmployeeCreationForm

    blanking_conditions = (
        (lambda req, obj: not req.user.is_superuser, ['is_admin', 'is_staff', 'user_permissions', 'groups']),
    )

    # @formatter:off
    list_display = (
        *HISAccountAdmin.list_display,
        *PERSON_LIST_DISPLAY,
        'department',
    )

    list_filter = (
        'department',
        # *PERSON_LIST_FILTER,
        *HISAccountAdmin.list_filter
    )

    fieldsets = (
        *ORG_FIELDSETS,
        *PERSON_FIELDSETS,
        *ADDRESS_FIELDSETS,
        *ACCOUNT_FIELDSETS
    )

    add_fieldsets = (
        *ORG_FIELDSETS,
        *PERSON_FIELDSETS,
        *ADDRESS_FIELDSETS,
        *ACCOUNT_ADD_FIELDSETS
    )
    # @formatter:on

    search_fields = PERSON_SEARCH_FIELDS + HISAccountAdmin.search_fields
    ordering = PERSON_ORDERING + HISAccountAdmin.ordering


class AdministrativeEmployeeAdmin(EmployeeAdmin):
    form = EmployeeChangeForm
    add_form = EmployeeCreationForm


class DoctorQualificationInline(admin.TabularInline):
    model = DoctorQualification
    extra = 1


class DoctorAdmin(EmployeeAdmin):
    inlines = (DoctorQualificationInline,)


class NurseAdmin(EmployeeAdmin):
    form = EmployeeChangeForm
    add_form = EmployeeCreationForm


class GeneralPersonnelCreationForm(EmployeeCreationForm):
    function = forms.ChoiceField(label=_('Funktion'), choices=GeneralPersonnel.Function.choices)

    class Meta:
        model = GeneralPersonnel
        fields = '__all__'


class GeneralPersonnelAdmin(EmployeeAdmin):
    form = EmployeeChangeForm
    add_form = GeneralPersonnelCreationForm

    # @formatter:off
    list_display = (
                       'function',
                   ) + EmployeeAdmin.list_display

    list_filter = (
                      'function',
                  ) + EmployeeAdmin.list_filter

    fieldsets = (
                    (_('Funktion'), {
                        'classes': ('wide',),
                        'fields': ('function',)
                    }),
                ) + EmployeeAdmin.fieldsets

    add_fieldsets = (
                        (_('Funktion'), {
                            'classes': ('wide',),
                            'fields': ('function',)
                        }),
                    ) + EmployeeAdmin.add_fieldsets
    # @formatter:on

    search_fields = ('function',) + EmployeeAdmin.search_fields
    ordering = ('function',) + EmployeeAdmin.ordering
