from HIS.models.common import TimeStamped, Closeable
from datetime import datetime, date
from django.db import models

from HIS.models.users import Employee, Patient


class Case(Closeable):
    case_id: int = models.IntegerField(primary_key=True)
    patient: Patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING)
    assigned_to_: Employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)
    assignment_history: ...


class Report(TimeStamped):
    report_id: int = models.IntegerField(primary_key=True)
    written_by: Employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)
    regarding: Case = models.ForeignKey(Case, on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True


class Order(Closeable):
    order_id: int = models.IntegerField(primary_key=True)
    issued_by: Employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)
    assigned_at: datetime = models.DateTimeField(null=True)
    assigned_to: Employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True
