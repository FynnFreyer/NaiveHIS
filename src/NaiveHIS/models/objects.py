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
