from django.db import models
from django.contrib.auth.models import AbstractUser
# from uuid import uuid4

from datetime import date

from HIS.models.common import TimeStamped


class User(AbstractUser, TimeStamped):
    ...

    class Meta(AbstractUser.Meta, TimeStamped.Meta):
        ...



class Patient(User):
    patient_id: int = models.IntegerField(primary_key=True)
    date_of_birth: date | None = models.DateField(null=True)

    class Meta(User.Meta):
        ordering = ['last_name']


class Employee(User):
    employee_id: int = models.IntegerField(primary_key=True)

    class Meta(User.Meta):
        ...
