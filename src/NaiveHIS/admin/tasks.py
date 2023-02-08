from django import forms
from django.contrib import admin
from django.contrib.admin import display
from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy as _

from .common import CLOSEABLE_FIELDSETS, CLOSEABLE_LIST_DISPLAY, TIMESTAMPED_LIST_DISPLAY
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
    _last_room,
    _next_room,
)


class CaseAdmin(admin.ModelAdmin):
    fieldsets = CASE_FIELDSETS + CLOSEABLE_FIELDSETS
    add_fieldsets = CASE_FIELDSETS + CLOSEABLE_FIELDSETS

    list_display = CASE_LIST_DISPLAY + CLOSEABLE_LIST_DISPLAY


def PrefilledFieldAdminMixin(field_name, field_value, eval_field_value=False, disabled=True):
    class Admin(admin.ModelAdmin):
        def get_form(self, request, obj=None, **kwargs):
            if eval_field_value:
                value = eval(field_value)
            else:
                value = field_value

            form = super().get_form(request, obj, **kwargs)

            form.base_fields[field_name].initial = value
            form.base_fields[field_name].disabled = disabled

            return form

    return Admin


ORDER_LIST_DISPLAY = (
    'assigned_to',
    'issued_by',
    'case',
)


def generate_order_fieldsets(*fields: tuple[str, ...]):
    return (
        (_('Auftragsdaten'), {
            'classes': ('wide',),
            'fields': (
                ('issued_by', 'case'),
                ('assigned_to',),
                ('assigned_at',),
                *fields,
                ('closed_at',),
            )
        }),
    )


class OrderAdmin(PrefilledFieldAdminMixin('issued_by', 'request.user.id', eval_field_value=True)):
    ...


_transport_field_sets = (
    ('from_room', 'to_room'),
    ('requested_arrival',),
    ('supervised', 'supervised_by'),
)

TRANSPORTORDER_FIELDSETS = generate_order_fieldsets(*_transport_field_sets)
TRANSPORTORDER_ADD_FIELDSETS = TRANSPORTORDER_FIELDSETS
TRANSPORTORDER_LIST_DISPLAY = tuple(field for fields in _transport_field_sets for field in fields)


class TransportOrderAdmin(OrderAdmin):
    fieldsets = TRANSPORTORDER_FIELDSETS
    add_fieldsets = TRANSPORTORDER_ADD_FIELDSETS

    list_display = TRANSPORTORDER_LIST_DISPLAY + ORDER_LIST_DISPLAY + CLOSEABLE_LIST_DISPLAY

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        transport_personnel = GeneralPersonnel.objects.filter(function='transport')
        form.base_fields['assigned_to'] = ModelChoiceField(queryset=transport_personnel,
                                                           required=False, label=_('Auftragnehmer'))

        return form


class TransferOrderAdmin(OrderAdmin):
    fieldsets = generate_order_fieldsets(('from_department', 'to_department'))
    add_fieldsets = generate_order_fieldsets(('from_department', 'to_department'))

    list_display = ('from_department', 'to_department') + ORDER_LIST_DISPLAY + CLOSEABLE_LIST_DISPLAY


class TreatmentOrderAdmin(OrderAdmin):
    fieldsets = generate_order_fieldsets(('doctor',))
    add_fieldsets = generate_order_fieldsets(('doctor',))

    list_display = ('doctor',) + ORDER_LIST_DISPLAY + CLOSEABLE_LIST_DISPLAY


class ExaminationOrderAdmin(OrderAdmin):
    fieldsets = generate_order_fieldsets(('description',))
    add_fieldsets = generate_order_fieldsets(('description',))

    list_display = ORDER_LIST_DISPLAY + CLOSEABLE_LIST_DISPLAY


# ACT_FIELDSETS = (
#     (_('Maßnahme'), {
#         'classes': ('wide',),
#         'fields': (
#             ('initiator', 'requesting_department'),
#             ('case',),
#             ('executing_department',),
#         )
#     }),
# )
#
# ACT_LIST_DISPLAY = (
#     'case',
#     'executing_department',
#     'requesting_department',
# )
#
#
# class ActAdmin(PrefilledFieldAdminMixin('initiator')):
#     fieldsets = ACT_FIELDSETS + CLOSEABLE_FIELDSETS
#     add_fieldsets = ACT_FIELDSETS + CLOSEABLE_FIELDSETS
#
#     list_display = ACT_LIST_DISPLAY + CLOSEABLE_LIST_DISPLAY


def generate_report_fieldsets(*fields: tuple[str, ...]):
    return (
        (_('Reportdaten'), {
            'classes': ('wide',),
            'fields': (
                ('written_by', 'case'),
                *fields
            )
        }),
    )


REPORT_FIELDSETS = generate_report_fieldsets()
REPORT_LIST_DISPLAY = ('case', 'written_by')


class ReportAdmin(PrefilledFieldAdminMixin('written_by', 'request.user.id', eval_field_value=True)):
    fieldsets = REPORT_FIELDSETS
    add_fieldsets = REPORT_FIELDSETS

    list_display = REPORT_LIST_DISPLAY + TIMESTAMPED_LIST_DISPLAY


class AnamnesisReportAdmin(ReportAdmin):
    fieldsets = generate_report_fieldsets(('text',))
    add_fieldsets = generate_report_fieldsets(('text',))

    list_display = ReportAdmin.list_display


class DiagnosisReportAdmin(ReportAdmin):
    fieldsets = generate_report_fieldsets(('text',))
    add_fieldsets = generate_report_fieldsets(('text',))

    list_display = ReportAdmin.list_display


class ExaminationReportAdmin(ReportAdmin):
    fieldsets = generate_report_fieldsets(('examination_order', 'text',))
    add_fieldsets = generate_report_fieldsets(('examination_order', 'text',))

    list_display = ('examination_order',) + ReportAdmin.list_display


class TherapyReportAdmin(ReportAdmin):
    fieldsets = generate_report_fieldsets(('text',))
    add_fieldsets = generate_report_fieldsets(('text',))

    list_display = ReportAdmin.list_display


class FindingsReportAdmin(ReportAdmin):
    fieldsets = generate_report_fieldsets(('diagnosis_report', 'therapy_report'), ('text',))
    add_fieldsets = generate_report_fieldsets(('diagnosis_report', 'therapy_report'), ('text',))

    list_display = ReportAdmin.list_display
