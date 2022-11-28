from .common import TimeStamped

from django.db import models


class Department(TimeStamped):
    department_id: int = models.IntegerField(primary_key=True)




class Room(TimeStamped):
    id: int = models.IntegerField(primary_key=True)
    division: Department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, null=True)
    capacity: int = models.IntegerField(validators=(lambda x: x > 0,))




