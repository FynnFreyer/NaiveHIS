from django.db import models
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from datetime import date

from .common import TimeStamped, Person
from .medical import Discipline


class Department(TimeStamped):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta(TimeStamped.Meta):
        verbose_name = _('Abteilung')
        verbose_name_plural = _('Abteilungen')


class DepartmentQualifications(TimeStamped):
    department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING, verbose_name=_('Abteilung'))
    qualification = models.CharField(max_length=64, choices=Discipline.choices, verbose_name=_('Qualifikation'))

    def __str__(self):
        return f"{self.department} {_('braucht')} {Discipline(self.qualification).label}"

    class Meta(TimeStamped.Meta):
        verbose_name = _('Abteilungsqualifikation')
        verbose_name_plural = _('Abteilungsqualifikationen')


class Patient(Person):
    date_of_birth: date | None = models.DateField(blank=True, null=True)

    class Meta(Person.Meta):
        ordering = ('last_name',)
        verbose_name = _('Patient')
        verbose_name_plural = _('Patienten')

class RoomManager(models.Manager):
    ...


class Room(TimeStamped):
    objects = RoomManager()
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

    class Meta(TimeStamped.Meta):
        verbose_name = _('Raum')
        verbose_name_plural = _('Räume')

