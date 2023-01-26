from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _

from ..models.common import Address, Person
from .common import PersonChangeForm, PersonCreationForm, PersonAdmin

from ..models.accounts import (
    HISAccount,
    Employee,
    AdministrativeEmployee,
    Doctor, DoctorQualification,
    Nurse,
    GeneralPersonnel
)

from ..models.objects import Department


class HISAccountChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admins
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = HISAccount
        fields = '__all__'


class HISAccountCreationForm(forms.ModelForm):
    """
    A form for creating new accounts.
    """

    username = forms.CharField(max_length=33, required=False)
    email = forms.EmailField(widget=forms.EmailInput, required=False)
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password_control = forms.CharField(label=_('Password confirmation'), widget=forms.PasswordInput)

    class Meta:
        model = HISAccount
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

        if not HISAccount.objects.is_valid_username(username):
            raise ValidationError(_('Invalid username'))

        return username

    def save(self, commit=True):
        user = super().save(commit=False)

        user = self.Meta.model.objects.create_user(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password_control'],
            commit=commit
        )

        return user


class HISAccountAdmin(UserAdmin):
    # The forms to add and change user instances
    form = HISAccountChangeForm
    add_form = HISAccountCreationForm

    list_display = (
        'username',
        'email',
        'is_staff',
        'is_admin',
        'is_active'
    )

    list_filter = (
        'is_admin',
        'is_staff',
        'is_active'
    )

    search_fields = ('email', 'username')
    ordering = ('username',)
    filter_horizontal = ()

    fieldsets = (
        (_('Account Informationen'), {
            'classes': ('wide',),
            'fields': (
                ('username', 'email'),
                ('password',)
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
        (_('Account Informationen'), {
            'classes': ('wide',),
            'fields': (
                ('username', 'email'),
                ('password', 'password_control')
            )
        }),
        (_('Status'), {
            'classes': ('collapse',),
            'fields': (
                ('is_staff', 'is_active', 'is_admin'),
            )
        }),
    )

    class Meta:
        ...


class EmployeeChangeForm(HISAccountChangeForm):
    class Meta(HISAccountChangeForm.Meta):
        model = Employee
        fields = '__all__'

    person = forms.ModelChoiceField(Person.objects, label=_('Person'))
    department = forms.ModelChoiceField(Department.objects, label=_('Abteilung'))
    rank = forms.ChoiceField(choices=Meta.model.Rank.choices, label=_('Rang'))


class EmployeeCreationForm(HISAccountCreationForm):
    # Account Data
    username = forms.CharField(max_length=33, required=False)
    # email = forms.EmailField(widget=forms.EmailInput, required=False)
    # password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    # password_control = forms.CharField(label=_('Password confirmation'), widget=forms.PasswordInput)

    # Address Data
    address = forms.ModelChoiceField(Address.objects, label=_('Adresse'), required=False)

    street = forms.CharField(max_length=64, label=_('Straße'), required=False)
    street_number = forms.IntegerField(label=_('Hausnummer'), required=False)
    city = forms.CharField(max_length=64, label=_('Stadt'), required=False)
    zip_code = forms.CharField(max_length=5, label=_('Postleitzahl'), required=False)

    # Person Data
    person = forms.ModelChoiceField(Person.objects, label=_('Person'), required=False)

    gender = forms.ChoiceField(label=_('Geschlecht'), required=False,
                               choices=(('m', _('männlich')),
                                        ('w', _('weiblich')),
                                        ('d', _('divers'))))

    title = forms.CharField(max_length=32, label=_('Titel'), required=False)
    first_name = forms.CharField(max_length=32, label=_('Vorname'), required=False)
    last_name = forms.CharField(max_length=32, label=_('Nachname'), required=False)

    # TODO when passing person, no address should be needed

    # order of validation is important
    # username might depend on person,
    # and person might depend on address.
    # also, cleaning depends on having the atomic parts available
    # before the potential foreign key reference
    field_order = [
        'street', 'street_number', 'city', 'zip_code', 'address',
        'gender', 'title', 'first_name', 'last_name', 'person',
        'username', 'email', 'password', 'password_control',
    ]

    def clean_address(self):
        existing_address = self.cleaned_data.get('address')

        street = self.cleaned_data.get('street')
        street_number = self.cleaned_data.get('street_number')
        city = self.cleaned_data.get('city')
        zip_code = self.cleaned_data.get('zip_code')

        required_args = [street, street_number, city, zip_code]

        if all(required_args):
            created_address = Address.objects.create(
                street=street,
                street_number=street_number,
                city=city,
                zip_code=zip_code,
            )
        else:
            created_address = None

        if not (existing_address or created_address):
            raise ValidationError(
                _('Entweder muss eine existierende Adresse angegeben, oder eine neue angelegt werden.'),
                code='invalid'
            )

        address = existing_address if existing_address else created_address
        self.cleaned_data['address'] = address

        return address

    def clean_person(self):
        existing_person = self.cleaned_data.get('person')

        gender = self.cleaned_data.get('gender')
        title = self.cleaned_data.get('title')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        address = self.cleaned_data.get('address')

        required_args = [gender, first_name, last_name]

        if all(required_args):
            created_person = Person.objects.create(
                gender=gender,
                title=title,
                first_name=first_name,
                last_name=last_name,
                address=address,
            )
        else:
            created_person = None

        if not (existing_person or created_person):
            raise ValidationError(
                _('Entweder muss eine existierende Person angegeben, oder eine neue angelegt werden.'),
                code='invalid'
            )

        person = existing_person if existing_person else created_person
        self.cleaned_data['person'] = person

        return person

    def clean_username(self):
        username = self.cleaned_data.get('username')

        person = self.cleaned_data['person']

        first_name = person.first_name
        last_name = person.last_name

        if not username:
            username = HISAccount.objects.get_valid_username(first_name, last_name)
        elif not HISAccount.objects.is_valid_username(username):
            raise ValidationError(_(f'Nutzer "{username}" existiert bereits.'), code='duplicate')

        self.cleaned_data['username'] = username

        return username

    def save(self, commit=True, **kwargs):
        employee = super().save(commit=False)

        address = self.cleaned_data['address']
        person = self.cleaned_data['person']

        employee = self.Meta.model.objects.create_user(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password_control'],
            person=self.cleaned_data['person'],
            department=self.cleaned_data['department'],
            rank=self.cleaned_data['rank'],
            **kwargs
        )

        if commit:
            address.save()
            person.save()
            employee.save()

        return employee

    class Meta:
        model = Employee
        fields = '__all__'


class EmployeeAdmin(HISAccountAdmin, PersonAdmin):
    form = EmployeeChangeForm
    add_form = EmployeeCreationForm

    # @formatter:off
    list_display = (
        'rank',
        'department',
    ) + PersonAdmin.list_display + HISAccountAdmin.list_display

    list_filter = (
        'rank',
        'department',
    ) + PersonAdmin.list_filter + HISAccountAdmin.list_filter

    fieldsets = (
        (_('Organisationseinheit'), {
            'classes': ('wide',),
            'fields': ('rank', 'department')
        }),
        (_('Persönliche Informationen'), {
            'classes': ('wide',),
            'fields': ('person',)
        }),
    ) + HISAccountAdmin.fieldsets

    add_fieldsets = (
        (_('Organisationseinheit'), {
            'classes': ('wide',),
            'fields': ('rank', 'department')
        }),
        (_('Persönliche Informationen'), {
            'classes': ('wide',),
            'fields': (
                'person',
                'gender',
                'title',
                ('first_name', 'last_name'),
            )
        }),
        (_('Wohnhaft'), {
            'classes': ('wide',),
            'fields': (
                'address',
                ('street', 'street_number'),
                ('zip_code', 'city'),
            )
        }),
    ) + HISAccountAdmin.add_fieldsets
    # @formatter:on

    search_fields = ('person__title', 'person__first_name', 'person__last_name') + HISAccountAdmin.search_fields
    ordering = ('person__last_name', 'person__first_name', 'person__title') + HISAccountAdmin.ordering

    class Meta(HISAccountAdmin.Meta, PersonAdmin.Meta):
        ...


class AdministrativeEmployeeChangeForm(EmployeeChangeForm):
    class Meta(EmployeeChangeForm.Meta):
        model = AdministrativeEmployee
        fields = '__all__'

    rank = forms.ChoiceField(choices=Meta.model.Rank.choices, label=_('Rang'))


class AdministrativeEmployeeCreationForm(EmployeeCreationForm):
    class Meta(EmployeeCreationForm.Meta):
        model = AdministrativeEmployee
        fields = '__all__'


class AdministrativeEmployeeAdmin(EmployeeAdmin):
    form = AdministrativeEmployeeChangeForm
    add_form = AdministrativeEmployeeCreationForm


class DoctorQualificationInline(admin.TabularInline):
    model = DoctorQualification
    extra = 3

    # TODO how to set the inline doctor to the doctor created by  the form?
    #  probs have to override the form


class DoctorChangeForm(EmployeeChangeForm):
    class Meta(EmployeeChangeForm.Meta):
        model = Doctor
        fields = '__all__'

    rank = forms.ChoiceField(choices=Meta.model.Rank.choices, label=_('Rang'))


class DoctorCreationForm(EmployeeCreationForm):
    class Meta(EmployeeCreationForm.Meta):
        model = Doctor
        fields = '__all__'

    # def save(self, commit=True):
    #     doctor = super().save(commit=False)
    #     doctor.savem2m()
    #
    #     doctor = Doctor(
    #
    #     )
    #
    #     if commit:
    #         doctor.save()
    #
    #     return doctor




class DoctorAdmin(EmployeeAdmin):
    inlines = (DoctorQualificationInline,)


class NurseChangeForm(EmployeeChangeForm):
    class Meta(EmployeeChangeForm.Meta):
        model = Nurse
        fields = '__all__'

    rank = forms.ChoiceField(choices=Meta.model.Rank.choices, label=_('Rang'))


class NurseCreationForm(EmployeeCreationForm):
    class Meta(EmployeeCreationForm.Meta):
        model = Nurse
        fields = '__all__'


class NurseAdmin(EmployeeAdmin):
    form = NurseChangeForm
    add_form = NurseCreationForm


class GeneralPersonnelChangeForm(EmployeeChangeForm):
    class Meta(EmployeeChangeForm.Meta):
        model = GeneralPersonnel
        fields = '__all__'

    rank = forms.ChoiceField(choices=Meta.model.Rank.choices, label=_('Rang'))


class GeneralPersonnelCreationForm(EmployeeCreationForm):
    function = forms.ChoiceField(label=_('Funktion'), choices=GeneralPersonnel.Function.choices)

    def save(self, commit=True):
        general_personnel = super().save(commit=False, function=self.cleaned_data['function'])

        if commit:
            general_personnel.save(using=self._db)

        return general_personnel

    class Meta:
        model = GeneralPersonnel
        fields = '__all__'


class GeneralPersonnelAdmin(EmployeeAdmin):
    form = GeneralPersonnelChangeForm
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
