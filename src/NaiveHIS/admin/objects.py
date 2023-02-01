from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .common import PERSON_FIELDSETS, ADDRESS_FIELDSETS, PERSON_LIST_DISPLAY, ADDRESS_LIST_DISPLAY
from ..models.common import AddressRequiredMixin, PersonMixin
from ..models.objects import Patient, Department, DepartmentQualifications, Room


class PatientAdmin(admin.ModelAdmin):
    fieldsets = (
        *PERSON_FIELDSETS,
        *ADDRESS_FIELDSETS,
    )

    add_fieldsets = fieldsets

    list_display = PERSON_LIST_DISPLAY + ADDRESS_LIST_DISPLAY


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
