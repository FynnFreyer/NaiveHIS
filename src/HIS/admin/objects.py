from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .common import PersonChangeForm, PersonCreationForm, PersonAdmin
from ..models.common import Address, Person
from ..models.objects import Patient, Department, DepartmentQualifications, Room


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

class RoomChangeForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'

class RoomCreationForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'

    def save(self, commit=True):
        room = super().save(commit=False)

        room = Room(
            name=self.cleaned_data['name'],
            department=self.cleaned_data['department'],
            capacity=self.cleaned_data['capacity'],
            usage=self.cleaned_data['usage'],
        )

        if commit:
            room.save()

        return room

class RoomAdmin(admin.ModelAdmin):
    form = RoomChangeForm
    add_form = RoomCreationForm
    
    list_display = (
        'name',
        'department',
        'capacity',
        'usage',
        'free_capacity'
    )

    class Meta:
        model = Room
        fields = '__all__'