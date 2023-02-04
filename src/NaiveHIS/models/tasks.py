from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib import admin

from datetime import datetime
from operator import attrgetter
from typing import Optional

from .common import TimeStampedMixin, CloseableMixin, CloseableManager
from .accounts import HISAccount, Employee, GeneralPersonnel, Doctor, AdministrativeEmployee
from .objects import Patient, Department, Room


class Case(CloseableMixin):
    objects = CloseableManager()

    patient: Patient = models.ForeignKey(to=Patient, on_delete=models.DO_NOTHING, verbose_name=_('Patient'))
    assigned_department: Department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING,
                                                        verbose_name=_('Verantwortliche Abteilung'))
    assigned_doctor: Doctor | None = models.ForeignKey(to=Doctor, on_delete=models.DO_NOTHING, blank=True, null=True,
                                                       verbose_name=_('Behandelnder Arzt'))

    def __str__(self):
        return f'Fall {self.id} vom {self.created_at.date()} betreffend {self.patient}'

    @property
    def last_room(self) -> Optional['Room']:
        closed_transports = TransportOrder.objects.closed_objects.filter(regarding__regarding=self)

        if closed_transports:
            last = closed_transports.order_by('-closed_at')[0]
            return last.to_room

        return None

    @property
    def next_room(self) -> Optional['Room']:
        open_transports = TransportOrder.objects.open_objects.filter(regarding__regarding=self)

        if open_transports:
            next = open_transports.order_by('requested_arrival')[0]
            return next.to_room

        return None

    # @property
    # def current_room(self) -> Optional['Room']:
    #     if self.last_room == self.next_room:
    #         return self.last_room
    #     return None

    class Meta(CloseableMixin.Meta):
        verbose_name = _('Fall')
        verbose_name_plural = _('Fälle')
        unique_together = ('patient', 'closed_at')


class Act(CloseableMixin):
    objects = CloseableManager()

    regarding: Case = models.ForeignKey(to=Case, on_delete=models.DO_NOTHING, verbose_name=_('Betroffener Fall'))
    initiator: HISAccount = models.ForeignKey(to=HISAccount, on_delete=models.DO_NOTHING, verbose_name=_('Initiator'))
    requesting_department: Department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING,
                                                          related_name='requesting_department',
                                                          verbose_name=_('Ersuchende Abteilung'))
    executing_department: Department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING,
                                                         related_name='executing_department',
                                                         verbose_name=_('Ausführende Abteilung'))

    def __str__(self):
        return f'Maßnahme {self.id} zu {self.regarding}'

    class Meta(CloseableMixin.Meta):
        verbose_name = _('Maßnahme')
        verbose_name_plural = _('Maßnahmen')


class Order(CloseableMixin):
    objects = CloseableManager()

    issued_by: HISAccount = models.ForeignKey(to=HISAccount, on_delete=models.DO_NOTHING,
                                              related_name='%(class)s_issuer', verbose_name=_('Auftraggeber'))
    assigned_to: HISAccount = models.ForeignKey(to=HISAccount, on_delete=models.DO_NOTHING, null=True,
                                                related_name='%(class)s_assignee', verbose_name=_('Auftragnehmer'))

    assigned_at: datetime = models.DateTimeField(blank=True, null=True, verbose_name=_('Zuweisungszeitpunkt'))
    regarding: Act = models.ForeignKey(to=Act, on_delete=models.DO_NOTHING, verbose_name=_('Betroffene Maßnahme'))

    def __str__(self):
        return f'Auftrag von {self.issued_by}, an {self.assigned_to}, betreffs {self.regarding}'

    class Meta:
        verbose_name = _('Auftrag')
        verbose_name_plural = _('Aufträge')
        abstract = True


class TransportOrder(Order):
    from_room: Room = models.ForeignKey(to=Room, on_delete=models.DO_NOTHING, related_name='from_room',
                                        verbose_name=_('Von'))
    to_room: Room = models.ForeignKey(to=Room, on_delete=models.DO_NOTHING, related_name='to_room',
                                      verbose_name=_('Nach'))
    requested_arrival: datetime = models.DateTimeField(verbose_name=_('Ankunftszeit'))
    supervised: bool = models.BooleanField(verbose_name=_('Beaufsichtigung notwendig'))
    supervised_by: Doctor = models.ForeignKey(to=Doctor, on_delete=models.DO_NOTHING, related_name='supervisor',
                                              verbose_name=_('Beaufsichtigt durch'), blank=True, null=True)

    def __str__(self):
        return f'Transportauftrag für {self.regarding.regarding.patient}, von {self.from_room}, nach {self.to_room}'

    class Meta(Order.Meta):
        verbose_name = _('Transport Auftrag')
        verbose_name_plural = _('Transport Aufträge')


class TransferOrder(Order):
    from_department: Department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING,
                                                    related_name='from_department', verbose_name=_('Von'))
    to_department: Department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING,
                                                  related_name='to_department', verbose_name=_('Nach'))

    class Meta(Order.Meta):
        verbose_name = _('Überweisungs Auftrag')
        verbose_name_plural = _('Überweisungs Aufträge')


class Assignment(Order):
    from_doctor: Doctor = models.ForeignKey(to=Doctor, null=True, on_delete=models.DO_NOTHING,
                                            related_name='from_doctor')
    to_doctor: Doctor = models.ForeignKey(to=Doctor, on_delete=models.DO_NOTHING, related_name='to_doctor')


class Report(TimeStampedMixin):
    written_by: HISAccount = models.ForeignKey(to=HISAccount, on_delete=models.DO_NOTHING, verbose_name=_('Author'))
    regarding: Act = models.ForeignKey(to=Act, on_delete=models.DO_NOTHING, verbose_name=_('Betroffener Fall'))

    class Meta:
        abstract = True


class AnamnesisReport(Report):
    anamnesis_text: str = models.TextField(verbose_name=_('Anamnese'))

    class Meta(Report.Meta):
        verbose_name = _('Anamnese-Report')
        verbose_name_plural = _('Anamnese-Reports')
