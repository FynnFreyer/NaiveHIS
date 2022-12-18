from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

from itertools import count

from .common import TimeStamped, Person
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
        for klass in [HISAccount, *Employee.__subclasses__()]:
            valid = False

            try:
                klass.objects.get(username=username)
            except klass.DoesNotExist:
                # if it doesn't exist we're happy
                valid = True

            if not valid:
                break

        return valid

    @staticmethod
    def all_accounts():
        qs = models.QuerySet()

        for klass in (HISAccount, *Employee.__subclasses__()):
            qs |= klass.objects.all()

        return qs.distinct()


class HISAccount(AbstractBaseUser, TimeStamped):
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
        return self.is_staff and self.is_active and self.is_admin

    class Meta:
        verbose_name = _('KIS Nutzer')
        verbose_name_plural = _('KIS Nutzer')


class EmployeeManager(HISAccountManager):
    def create_user(self, username=None, email=None, password=None,
                    person=None, department=None, rank=None):

        username = self.get_valid_username(first_name=person.first_name, last_name=person.last_name) \
            if not username else username

        user = super().create_user(username=username, email=email, password=None, commit=False)

        user.person = person
        user.department = department
        user.rank = rank

        return user


# TODO over
class Employee(HISAccount):
    class Rank(models.TextChoices):
        ...

    person = models.OneToOneField(to=Person, on_delete=models.DO_NOTHING, verbose_name=_('Person'))
    department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING, verbose_name=_('Abteilung'))
    rank = models.CharField(max_length=64, verbose_name=_('Rang'))

    class Meta:
        abstract = True


class AdministrativeEmployeeManager(EmployeeManager):
    def create_user(self, username=None, email=None, password=None,
                    person=None, department=None, rank=None, commit=True):
        user = super().create_user(username=username, email=email, password=password,
                                   person=person, department=department, rank=rank)
        
        administrative_employee = AdministrativeEmployee(
            username=user.username, 
            email=user.email, 
            password=user.password,
            person=user.person, 
            department=user.department, 
            rank=user.rank
        )
        
        if commit:
            administrative_employee.save(using=self._db)
            
        return administrative_employee

class AdministrativeEmployee(Employee):
    objects = AdministrativeEmployeeManager()

    class Rank(models.TextChoices):
        CEO = ('ceo', _('Geschäftsführung'))
        MEDICAL_DIRECTOR = ('medical_director', _('Ärztliche Leitung'))
        NURSING_DIRECTOR = ('nursing_director', _('Pflegerische Leitung'))
        TEAM_LEAD = ('team_lead', _('Teamleitung'))
        EMPLOYEE = ('employee', _('Angestellte_r'))

    rank = models.CharField(max_length=64, choices=Rank.choices, verbose_name=_('Rang'))

    class Meta:
        verbose_name = _('Verwaltungsangestellte_r')
        verbose_name_plural = _('Verwaltungsangestellte')


class DoctorManager(EmployeeManager):
    def create_user(self, username=None, email=None, password=None,
                    person=None, department=None, rank=None, commit=True):
        
        user = super().create_user(username=username, email=email, password=password,
                                   person=person, department=department, rank=rank)

        doctor = Doctor(
            username=user.username,
            email=user.email,
            password=user.password,
            person=user.person,
            department=user.department,
            rank=user.rank
        )

        if commit:
            doctor.save(using=self._db)

        return doctor


class Doctor(Employee):
    objects = DoctorManager()

    class Rank(models.TextChoices):
        CHIEF_PHYSICIAN = ('chief', _('Chefärztliches Personal'))
        SENIOR_PHYSICIAN = ('senior', _('Oberärztliches Personal'))
        SPECIALIST_PHYSICIAN = ('specialist', _('Fachärztliches Personal'))
        JUNIOR_PHYSICIAN = ('junior', _('Assistenzärztliches Personal'))

    rank = models.CharField(max_length=64, choices=Rank.choices, verbose_name=_('Rang'))

    @property
    @admin.display(description=_('Qualifikationen'))
    def qualifications(self):
        return [dq.qualification for dq in DoctorQualification.objects.filter(doctor=self)]

    class Meta:
        verbose_name = _('Arzt/Ärztin')
        verbose_name_plural = _('Ärzte')


class DoctorQualification(TimeStamped):
    doctor = models.ForeignKey(to=Doctor, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=64, choices=Discipline.choices)

    class Meta:
        verbose_name = _('Ärztliche Qualifikation')
        verbose_name_plural = _('Ärztliche Qualifikationen')


class NurseManager(EmployeeManager):
    def create_user(self, username=None, email=None, password=None,
                    person=None, department=None, rank=None, commit=True):
        user = super().create_user(username=username, email=email, password=password,
                                   person=person, department=department, rank=rank)

        nurse = Nurse(
            username=user.username,
            email=user.email,
            password=user.password,
            person=user.person,
            department=user.department,
            rank=user.rank
        )

        if commit:
            nurse.save(using=self._db)

        return nurse


class Nurse(Employee):
    objects = NurseManager()

    class Rank(models.TextChoices):
        LEAD_NURSE = ('lead', _('Stationsleitung Pflege'))
        TRAINED_NURSE = ('trained', _('Pflegefachpersonal'))
        NURSING_HELP = ('helper', _('Krankenpflegehilfspersonal'))
        NURSING_STUDENT = ('learner', _('Krankenpflege-Azubi'))
        NURSING_INTERN = ('intern', _('Krankenpflege-Praktikant_in'))

    rank = models.CharField(max_length=64, choices=Rank.choices, verbose_name=_('Rang'))

    class Meta:
        verbose_name = _('Krankenpflegekraft')
        verbose_name_plural = _('Krankenpflegekräfte')



class GeneralPersonnelManager(EmployeeManager):
    def create_user(self, username=None, email=None, password=None,
                    person=None, department=None, rank=None, function=None, commit=True):

        user = super().create_user(username=username, email=email, password=password,
                                   person=person, department=department, rank=rank)

        # if not function in GeneralPersonnel.Function:
        #     raise ValueError(_('Sonstige Beschäftigte brauchen eine Funktion'))

        general_personnel = GeneralPersonnel(
            username=user.username,
            email=user.email,
            password=user.password,
            person=user.person,
            department=user.department,
            rank=user.rank,
            function=function
        )

        if commit:
            general_personnel.save(using=self._db)

        return general_personnel


class GeneralPersonnel(Employee):
    objects = GeneralPersonnelManager()

    class Rank(models.TextChoices):
        TEAM_LEAD = ('team_lead', _('Teamleitung'))
        EMPLOYEE = ('employee', _('Angestellte_r'))

    class Function(models.TextChoices):
        TRANSPORT = ('transport', _('Transport'))
        CLEANING = ('cleaning', _('Raumpflege'))

    rank = models.CharField(max_length=64, choices=Rank.choices, verbose_name=_('Rang'))
    function = models.CharField(max_length=64, choices=Function.choices, verbose_name=_('Funktion'))

    class Meta:
        verbose_name = _('Sonstige_r Beschäftigte_r')
        verbose_name_plural = _('Sonstige Beschäftigte')
