from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .common import PersonChangeForm, PersonCreationForm, PersonAdmin
from ..models.common import Address, Person
from ..models.objects import Patient, Department, DepartmentQualifications


class PatientChangeForm(PersonChangeForm):
    class Meta:  # (PersonChangeForm.Meta):
        model = Patient
        fields = '__all__'


class PatientCreationForm(PersonCreationForm):
    date_of_birth = forms.DateField(required=False)

    class Meta:  # (PersonCreationForm.Meta):
        model = Patient
        fields = '__all__'

    def save(self, commit=True):
        patient = super().save(commit=False)

        patient = Patient(
            gender=patient.gender,
            title=patient.title,
            first_name=patient.first_name,
            last_name=patient.last_name,
            address=patient.address,
            date_of_birth=self.cleaned_data['date_of_birth']
        )

        if commit:
            patient.save()

        return patient


class PatientAdmin(admin.ModelAdmin):
    form = PatientChangeForm
    add_form = PatientCreationForm

    fieldsets = (
        (_('Persönliche Informationen'), {
            'classes': ('wide',),
            'fields': (
                ('gender', 'date_of_birth'),
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

