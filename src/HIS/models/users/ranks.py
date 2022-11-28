from django.db import models

from HIS.models.users import Employee
from HIS.models.objects import Department


RANKS = (
    ('ceo', 'Geschäftsführung'),
    ('medical_director', 'Ärztliche Leitung'),
    ('chief_physician', 'Chefärztliches Personal'),
    ('senior_physician', 'Oberärztliches Personal'),
    ('specialist_physician', 'Fachärztliches Personal'),
    ('junior_physician', 'Assistenzärztliches Personal'),
    ('team_lead', 'Teamleitung'),
    ('employee', 'Angestellte_r')
)


class Position(models.Model):
    held_by: Employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, primary_key=True)
    held_at: Department | None = models.ForeignKey(Department, on_delete=models.DO_NOTHING, null=True)
    rank: str = models.CharField(max_length=16, choices=RANKS)

