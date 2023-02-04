from django import forms
from django.contrib import admin
from django.contrib.admin import display
from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy as _

from .common import CLOSEABLE_FIELDSETS, CLOSEABLE_LIST_DISPLAY
from ..models.accounts import GeneralPersonnel
from ..models.tasks import Case

CASE_FIELDSETS = (
    (_('Falldaten'), {
        'classes': ('wide',),
        'fields': (
            ('patient',),
            ('assigned_department', 'assigned_doctor'),
        )
    }),
)


@display(description=_('Letzter Aufenthaltsort'))
def _last_room(obj: Case):
    return obj.last_room


@display(description=_('Nächster Aufenthaltsort'))
def _next_room(obj: Case):
    return obj.next_room


CASE_LIST_DISPLAY = (
    'patient',
    'assigned_department',
    'assigned_doctor',
    'last_room',
    'next_room',
)


class CaseAdmin(admin.ModelAdmin):
    fieldsets = CASE_FIELDSETS + CLOSEABLE_FIELDSETS
    add_fieldsets = CASE_FIELDSETS + CLOSEABLE_FIELDSETS

    list_display = CASE_LIST_DISPLAY + CLOSEABLE_LIST_DISPLAY


def PrefilledIDAdminMixin(field_name, disabled=True):
    class Admin(admin.ModelAdmin):
        def get_form(self, request, obj=None, **kwargs):
            form = super().get_form(request, obj, **kwargs)

            form.base_fields[field_name].initial = request.user.id
            form.base_fields[field_name].disabled = True

            return form
    return Admin


ORDER_LIST_DISPLAY = (
    'assigned_to',
    'issued_by',
    'regarding',
)


def generate_order_fieldsets(*fields: tuple[str, ...], add=False):
    return (
        (_('Auftragsdaten'), {
            'classes': ('wide',),
            'fields': (
                ('issued_by', 'regarding'),
                ('assigned_to', 'assigned_at'),
                *fields,
                ('closed_at',),
            )
        }),
    )


def generate_order_add_fieldsets(*fields: tuple[str, ...]):
    return generate_order_fieldsets(*fields, add=True)


_transport_field_sets = (
    ('from_room', 'to_room'),
    ('requested_arrival',),
    ('supervised', 'supervised_by'),
)

TRANSPORTORDER_FIELDSETS = generate_order_fieldsets(*_transport_field_sets)
TRANSPORTORDER_ADD_FIELDSETS = generate_order_add_fieldsets(*_transport_field_sets)
TRANSPORTORDER_LIST_DISPLAY = tuple(field for fields in _transport_field_sets for field in fields)


class TransportOrderAdmin(PrefilledIDAdminMixin('issued_by')):
    fieldsets = TRANSPORTORDER_FIELDSETS
    add_fieldsets = TRANSPORTORDER_ADD_FIELDSETS

    list_display = TRANSPORTORDER_LIST_DISPLAY + ORDER_LIST_DISPLAY + CLOSEABLE_LIST_DISPLAY

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        transport_personnel = GeneralPersonnel.objects.filter(function='transport')
        form.base_fields['assigned_to'] = ModelChoiceField(queryset=transport_personnel)

        return form


ACT_FIELDSETS = (
    (_('Maßnahme'), {
        'classes': ('wide',),
        'fields': (
            ('initiator', 'requesting_department'),
            ('regarding',),
            ('executing_department',),
        )
    }),
)

ACT_LIST_DISPLAY = (
    'regarding',
    'executing_department',
    'requesting_department',
)


class ActAdmin(PrefilledIDAdminMixin('initiator')):
    fieldsets = ACT_FIELDSETS + CLOSEABLE_FIELDSETS
    add_fieldsets = ACT_FIELDSETS + CLOSEABLE_FIELDSETS

    list_display = ACT_LIST_DISPLAY + CLOSEABLE_LIST_DISPLAY
