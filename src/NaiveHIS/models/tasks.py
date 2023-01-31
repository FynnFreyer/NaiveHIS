from django.db import models
from django.utils.translation import gettext_lazy as _

from datetime import datetime

from .common import TimeStampedModel, CloseableModel
from .accounts import HISAccount, Employee, GeneralPersonnel, Doctor, AdministrativeEmployee
from .objects import Patient, Department, Room


class Case(CloseableModel):
    patient: Patient = models.ForeignKey(to=Patient, on_delete=models.DO_NOTHING)
    assigned_department: Department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING)
    assigned_doctor: Doctor | None = models.ForeignKey(to=Doctor, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta(CloseableModel.Meta):
        verbose_name = _('Fall')
        verbose_name_plural = _('Fälle')


class Act(CloseableModel):
    regarding: Case = models.ForeignKey(to=Case, on_delete=models.DO_NOTHING)
    initiator: HISAccount = models.ForeignKey(to=HISAccount, on_delete=models.DO_NOTHING)
    recipient: Department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING)

    class Meta(CloseableModel.Meta):
        verbose_name = _('Maßnahme')
        verbose_name_plural = _('Maßnahmen')


class Order(CloseableModel):
    issued_by: HISAccount = models.ForeignKey(to=HISAccount, on_delete=models.DO_NOTHING,
                                              related_name='%(class)s_issuer')
    assigned_to: HISAccount = models.ForeignKey(to=HISAccount, on_delete=models.DO_NOTHING, blank=True, null=True,
                                                related_name='%(class)s_assignee')

    assigned_at: datetime = models.DateTimeField(blank=True, null=True)
    regarding: Act = models.ForeignKey(to=Act, on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True


class TransportOrder(Order):
    from_room: Room = models.ForeignKey(to=Room, on_delete=models.DO_NOTHING, related_name='from_room')
    to_room: Room = models.ForeignKey(to=Room, on_delete=models.DO_NOTHING, related_name='to_room')
    requested_arrival_by: datetime = models.DateTimeField()
    supervised: bool = models.BooleanField()
    supervised_by: Doctor = models.ForeignKey(to=Doctor, on_delete=models.DO_NOTHING, related_name='supervisor')

    class Meta(Order.Meta):
        verbose_name = _('Transport Auftrag')
        verbose_name_plural = _('Transport Aufträge')


class TransferOrder(Order):
    from_department: Department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING,
                                                    related_name='from_department')
    to_department: Department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING,
                                                  related_name='to_department')

    class Meta(Order.Meta):
        verbose_name = _('Überweisungs Auftrag')
        verbose_name_plural = _('Überweisungs Aufträge')


class Report(TimeStampedModel):
    written_by: HISAccount = models.ForeignKey(to=HISAccount, on_delete=models.DO_NOTHING)
    regarding: Act = models.ForeignKey(to=Act, on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True


class AnamnesisReport(Report):
    anamnesis_text: str = models.TextField()

    class Meta(Report.Meta):
        verbose_name = _('Anamnese-Report')
        verbose_name_plural = _('Anamnese-Reports')
