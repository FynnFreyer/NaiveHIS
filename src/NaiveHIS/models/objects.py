from operator import attrgetter
from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _

from .common import TimeStampedMixin, PersonMixin, AddressOptionalMixin
from .medical import Discipline


class Department(TimeStampedMixin):
    name = models.CharField(max_length=64)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta(TimeStampedMixin.Meta):
        verbose_name = _('Abteilung')
        verbose_name_plural = _('Abteilungen')


class DepartmentQualifications(TimeStampedMixin):
    department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING, verbose_name=_('Abteilung'))
    qualification = models.CharField(max_length=64, choices=Discipline.choices, verbose_name=_('Qualifikation'))

    def __str__(self):
        return f"{self.department} {_('braucht')} {Discipline(self.qualification).label}"

    class Meta(TimeStampedMixin.Meta):
        verbose_name = _('Abteilungsqualifikation')
        verbose_name_plural = _('Abteilungsqualifikationen')


class PatientManager(models.Manager):
    def cases(self):
        ...


class Patient(PersonMixin, AddressOptionalMixin):
    @property
    def open_cases(self) -> list['Case']:
        return sorted([case for case in self.case_set.all() if case.is_open], key=attrgetter('opened_at'))

    @property
    def closed_cases(self) -> list['Case']:
        return sorted([case for case in self.case_set.all() if case.is_closed], key=attrgetter('closed_at'))

    @property
    def last_room(self) -> Optional['Room']:
        latest_open_case = self.open_cases[-1] if self.open_cases else None
        latest_open_case.objects.filter()
        raise NotImplemented

    @property
    def next_room(self) -> Optional['Room']:
        open_transports = self.case_set.filter(is_open=True, act__transportorder__is_closed=False)
        raise NotImplemented

    @property
    def is_in_transit_or_not_in_house(self) -> bool:
        return self.last_room != self.next_room

    @property
    def current_room(self) -> Optional['Room']:
        if self.last_room == self.next_room:
            return self.last_room
        return None

    class Meta:
        ordering = ('last_name',)
        verbose_name = _('Patient_in')
        verbose_name_plural = _('Patienten')


Patient._meta.get_field('date_of_birth').required = False
Patient._meta.get_field('date_of_birth').blank = True
Patient._meta.get_field('date_of_birth').null = True
Patient._meta.get_field('date_of_birth').default = None


class Room(TimeStampedMixin):
    name = models.CharField(max_length=64)
    department: Department = models.ForeignKey(Department, on_delete=models.DO_NOTHING,
                                               blank=True, null=True)
    capacity: int = models.IntegerField()
    usage: int = models.IntegerField(default=0)

    @property
    def is_capacity_available(self):
        return self.usage < self.capacity

    @property
    def free_capacity(self):
        return self.capacity - self.usage

    def __str__(self):
        return self.name

    class Meta(TimeStampedMixin.Meta):
        verbose_name = _('Raum')
        verbose_name_plural = _('Räume')
