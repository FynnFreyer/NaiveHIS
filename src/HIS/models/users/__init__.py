from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

from datetime import date
from itertools import count

from HIS.models.common import TimeStamped


class HISUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, title=None, username=None, password=None, commit=True):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)

        username = HISUser.normalize_username(self.get_valid_username(first_name, last_name)
                                              if not username else username)

        title = '' if title is None else title

        user = HISUser(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            title=title
        )

        user.set_password(password)

        if commit:
            user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name, last_name, title=None, username=None, password=None):
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            title=title,
            username=username,
            password=password
        )

        user.is_admin = True
        user.save()
        return user

    def get_valid_username(self, first_name, last_name):
        # usernames are generated from first char of first name and last name
        username_base = HISUser.normalize_username(first_name[0] + last_name).lower()
        # we have to check whether usernames are unique,
        # if they are not, we append an incrementing number

        username_try = username_base
        for i in count():
            # if we found a name, we are done here
            if self.is_valid_username(username_try):
                username = username_try
                break
            else:
                # otherwise we increment username_try
                username_try = username_base + str(i)

        return username

    def is_valid_username(self, username):
        valid = False

        try:
            self.get(username=username)
        except HISUser.DoesNotExist:
            # if it doesn't exist we're happy
            valid = True
        except:
            # if anything else went wrong, we're not
            pass

        return valid


class HISUser(AbstractBaseUser, TimeStamped):
    objects = HISUserManager()

    email = models.EmailField(unique=True, verbose_name=_('Email address'))
    username = models.CharField(max_length=33, unique=True, verbose_name=_('Username'))

    title = models.CharField(max_length=5, blank=True, verbose_name=_('Title'))
    first_name = models.CharField(max_length=32, verbose_name=_('First name'))
    last_name = models.CharField(max_length=32, verbose_name=_('Last name'))

    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'last_name', 'first_name')

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.title + ' ' if self.title else '' + self.first_name + self.last_name

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    class Meta(AbstractBaseUser.Meta, TimeStamped.Meta):
        verbose_name = _('HIS User')
        verbose_name_plural = _('HIS Users')


class Patient(HISUser):
    patient_id: int = models.IntegerField(primary_key=True)
    date_of_birth: date | None = models.DateField(null=True)

    is_staff = False
    is_active = False

    class Meta(HISUser.Meta):
        ordering = ('last_name',)
        verbose_name = _('Patient')
        verbose_name_plural = _('Patients')


class Function(models.Model):
    ...


class Department(models.Model):
    ...


class Rank(models.Model):
    ...


class Employee(HISUser):
    employee_id: int = models.IntegerField(primary_key=True)
    function = models.ForeignKey(to=Function, on_delete=models.DO_NOTHING)
    department = models.ForeignKey(to=Department, on_delete=models.DO_NOTHING)
    rank = models.ForeignKey(to=Rank, on_delete=models.DO_NOTHING)
    class Meta(HISUser.Meta):
        verbose_name = _('Employee')
        verbose_name_plural = _('Employee')


