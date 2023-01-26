from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models.common import Address, Person


# class PersonCreationForm(forms.ModelForm):
#     """
#     A form for creating new people.
#     """
#     class Meta:
#         model = Person
#         fields = '__all__'
#
# (_('Personal info'), {
#     'classes': ('wide',),
#     'fields': (
#         'title',
#         ('first_name', 'last_name')
#     )
# }),


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'

    def save(self, commit=True):
        address = super().save(commit=False)

        address = self.Meta.model.objects.create(
            street=self.cleaned_data['street'],
            street_number=self.cleaned_data['street_number'],
            city=self.cleaned_data['city'],
            zip_code=self.cleaned_data['zip_code']
        )

        if commit:
            address.save()

        return address


class AddressAdmin(admin.ModelAdmin):
    form = AddressForm

    model = Address
    fieldsets = (
        (_('Adresse'), {
            'classes': ('wide',),
            'fields': (
                ('street', 'street_number'),
                ('zip_code', 'city')
            )
        }),
    )


class PersonChangeForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = '__all__'


class PersonCreationForm(forms.ModelForm):
    address = forms.ModelChoiceField(Address.objects, required=False)

    class Meta:
        model = Person
        fields = '__all__'

    def save(self, commit=True):
        person = super().save(commit=False)

        person = self.Meta.model.objects.create(
            gender=person.gender,
            title=person.title,
            first_name=person.first_name,
            last_name=person.last_name,
            address=person.address,
        )

        if commit:
            person.save()

        return person


class PersonAdmin(admin.ModelAdmin):
    form = PersonChangeForm
    add_form = PersonCreationForm

    model = Person

    fieldsets = (
        (_('Persönliche Informationen'), {
            'classes': ('wide',),
            'fields': (
                'gender',
                'title',
                ('first_name', 'last_name'),
            )
        }),
        (_('Wohnhaft'), {
            'classes': ('wide',),
            'fields': (
                'address',
            )
        })
    )

    add_fieldsets = fieldsets

    class Meta:
        ...


def person_inline_factory(reverse_accessor):
    class PersonInline(admin.StackedInline):
        model = Person.__dict__[reverse_accessor + '_set']
        fieldsets = PersonAdmin.fieldsets + AddressAdmin.fieldsets

    return PersonInline

