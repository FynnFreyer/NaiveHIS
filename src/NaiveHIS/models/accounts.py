from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

from itertools import count

from .common import TimeStampedModel, PersonMixin, AddressRequiredMixin
from .objects import Department
from .medical import Discipline


class HISAccountManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, commit=True):
        if not username:
            raise ValueError(_('Accounts brauchen einen gültigen Accountnamen'))

        username = HISAccount.normalize_username(username)
        email = self.normalize_email(email) if email else None

        user = HISAccount(
            username=username,
            email=email,
        )

        user.set_password(password)

        if commit:
            user.save(using=self._db)

        return user

    def create_superuser(self, username, email=None, password=None, commit=True):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
            commit=commit,
        )

        user.is_admin = True

        if commit:
            user.save()

        return user

    def get_valid_username(self, first_name, last_name):
        # usernames are generated from first char of first name and last name
        username_base = HISAccount.normalize_username(first_name[0] + last_name).lower()
        # we have to check whether usernames are unique,
        # if they are not, we append an incrementing number

        username_guess = username_base
        for i in count():
            # if we found a name, we are done here
            if self.is_valid_username(username_guess):
                username = username_guess
                break
            else:
                # otherwise we generate a new guess (+ 1 for to avoid zero indexing)
                username_guess = username_base + str(i + 1)

        return username

    def is_valid_username(self, username):
        return not(self.all().filter(username=username))


class HISAccount(AbstractBaseUser, TimeStampedModel):
    objects = HISAccountManager()

    username = models.CharField(max_length=33, unique=True, verbose_name=_('Username'))
    email = models.EmailField(unique=True, null=True, verbose_name=_('Email address'))

    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_staff and self.is_active and self.is_admin

    def has_module_perms(self, app_label):
        return self.is_staff and self.is_active

    class Meta:
        verbose_name = _('KIS Nutzer')
        verbose_name_plural = _('KIS Nutzer')


def EmployeeManagerFactory(klass):
    class EmployeeManager(HISAccountManager):
        def create_user(self, username=None, email=None, password=None,
                        gender=None, title=None, first_name=None, last_name=None,
                        city=None, street=None, street_number=None, zip_code=None,
                        department=None, rank=None, commit=True, *args, **kwargs):
            username = self.get_valid_username(
                first_name=first_name,
                last_name=last_name
            ) if not username else username

            account = super().create_user(username=username, email=email, password=password, commit=False)

            employee = klass(
                username=account.username, email=account.email, password=account.password,
                gender=gender, title=title, first_name=first_name, last_name=last_name,
                city=city, street=street, street_number=street_number, zip_code=zip_code,
                department=department, rank=rank, *args, **kwargs
            )

            if commit:
                employee.save(using=employee.objects._db)

            return employee

    return EmployeeManager


class Employee(HISAccount, PersonMixin, AddressRequiredMixin):
    department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING, verbose_name=_('Abteilung'))
    rank = models.CharField(max_length=64, verbose_name=_('Rang'))

    class Meta:
        verbose_name = _('Angestellte_r')
        verbose_name_plural = _('Angestellte')
        abstract = True


class AdministrativeEmployee(Employee):
    class Rank(models.TextChoices):
        CEO = ('ceo', _('Geschäftsführung'))
        MEDICAL_DIRECTOR = ('medical_director', _('Ärztliche Leitung'))
        NURSING_DIRECTOR = ('nursing_director', _('Pflegerische Leitung'))
        TEAM_LEAD = ('team_lead', _('Teamleitung'))
        EMPLOYEE = ('employee', _('Angestellte_r'))

    class Meta:
        verbose_name = _('Verwaltungsangestellte_r')
        verbose_name_plural = _('Verwaltungsangestellte')


AdministrativeEmployee.objects = EmployeeManagerFactory(AdministrativeEmployee)()
AdministrativeEmployee._meta.get_field('rank').choices = AdministrativeEmployee.Rank.choices


class Doctor(Employee):
    class Rank(models.TextChoices):
        CHIEF_PHYSICIAN = ('chief', _('Chefärztliches Personal'))
        SENIOR_PHYSICIAN = ('senior', _('Oberärztliches Personal'))
        SPECIALIST_PHYSICIAN = ('specialist', _('Fachärztliches Personal'))
        JUNIOR_PHYSICIAN = ('junior', _('Assistenzärztliches Personal'))

    @property
    @admin.display(description=_('Qualifikationen'))
    def qualifications(self):
        return [dq.qualification for dq in DoctorQualification.objects.filter(doctor=self)]

    class Meta:
        verbose_name = _('Arzt/Ärztin')
        verbose_name_plural = _('Ärzte')


Doctor.objects = EmployeeManagerFactory(Doctor)()
Doctor._meta.get_field('rank').choices = Doctor.Rank.choices


class DoctorQualification(TimeStampedModel):
    doctor = models.ForeignKey(to=Doctor, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=64, choices=Discipline.choices)

    class Meta:
        verbose_name = _('Ärztliche Qualifikation')
        verbose_name_plural = _('Ärztliche Qualifikationen')


class Nurse(Employee):
    class Rank(models.TextChoices):
        LEAD_NURSE = ('lead', _('Stationsleitung Pflege'))
        TRAINED_NURSE = ('trained', _('Pflegefachpersonal'))
        NURSING_HELP = ('helper', _('Krankenpflegehilfspersonal'))
        NURSING_STUDENT = ('learner', _('Krankenpflege-Azubi'))
        NURSING_INTERN = ('intern', _('Krankenpflege-Praktikant_in'))

    class Meta:
        verbose_name = _('Krankenpflegekraft')
        verbose_name_plural = _('Krankenpflegekräfte')


Nurse.objects = EmployeeManagerFactory(Nurse)()
Nurse._meta.get_field('rank').choices = Nurse.Rank.choices


class GeneralPersonnel(Employee):
    class Rank(models.TextChoices):
        TEAM_LEAD = ('team_lead', _('Teamleitung'))
        EMPLOYEE = ('employee', _('Angestellte_r'))

    class Function(models.TextChoices):
        TRANSPORT = ('transport', _('Transport'))
        CLEANING = ('cleaning', _('Raumpflege'))

    function = models.CharField(max_length=64, choices=Function.choices, verbose_name=_('Funktion'))

    class Meta:
        verbose_name = _('Sonstige_r Beschäftigte_r')
        verbose_name_plural = _('Sonstige Beschäftigte')

GeneralPersonnel.objects = EmployeeManagerFactory(GeneralPersonnel)()
GeneralPersonnel._meta.get_field('rank').choices = GeneralPersonnel.Rank.choices
