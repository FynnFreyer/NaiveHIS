from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .common import CLOSEABLE_FIELDSETS, CLOSEABLE_LIST_DISPLAY

CASE_FIELDSETS = (
    (_('Falldaten'), {
        'classes': ('wide',),
        'fields': (
            ('patient',),
            ('assigned_department', 'assigned_doctor'),
        )
    }),
)

CASE_LIST_DISPLAY = (
    'patient',
    'assigned_department',
    'assigned_doctor',
)


class CaseAdmin(admin.ModelAdmin):
    fieldsets = CASE_FIELDSETS + CLOSEABLE_FIELDSETS
    add_fieldsets = CASE_FIELDSETS + CLOSEABLE_FIELDSETS

    list_display = CASE_LIST_DISPLAY + CLOSEABLE_LIST_DISPLAY


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
                ((('issued_by', 'regarding'),) if add else ()),
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
    ('requested_arrival_by',),
    ('supervised', 'supervised_by'),
)

TRANSPORTORDER_FIELDSETS = generate_order_fieldsets(*_transport_field_sets)
TRANSPORTORDER_ADD_FIELDSETS = generate_order_add_fieldsets(*_transport_field_sets)
TRANSPORTORDER_LIST_DISPLAY = tuple(field for fields in _transport_field_sets for field in fields)


class TransportOrderAdmin(admin.ModelAdmin):
    fieldsets = TRANSPORTORDER_FIELDSETS
    add_fieldsets = TRANSPORTORDER_ADD_FIELDSETS

    list_display = TRANSPORTORDER_LIST_DISPLAY + ORDER_LIST_DISPLAY + CLOSEABLE_LIST_DISPLAY


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


class ActAdmin(admin.ModelAdmin):
    fieldsets = ACT_FIELDSETS + CLOSEABLE_FIELDSETS
    add_fieldsets = ACT_FIELDSETS + CLOSEABLE_FIELDSETS

    list_display = ACT_LIST_DISPLAY + CLOSEABLE_LIST_DISPLAY
