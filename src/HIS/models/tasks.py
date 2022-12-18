from HIS.models.common import TimeStamped, Closeable
from datetime import datetime
from django.db import models

from .accounts import Employee
from .objects import Patient, Department


class Case(Closeable):
    patient: Patient = models.ForeignKey(to=Patient, on_delete=models.DO_NOTHING)
    assigned_department: Department = models.ForeignKey(to=Employee, on_delete=models.DO_NOTHING)
    assigned_personnel: list[Employee] = models.ManyToManyField(to=Employee)
    assignment_history: ...


class Act(Closeable):
    regarding: Case = models.ForeignKey(Case, on_delete=models.DO_NOTHING)


class Order(Closeable):
    issued_by: Employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)
    assigned_at: datetime = models.DateTimeField(null=True)
    assigned_to: Employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)
    regarding: Act = models.ForeignKey(Act, on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True


class Report(TimeStamped):
    written_by: Employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)
    regarding: Act = models.ForeignKey(Act, on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True


