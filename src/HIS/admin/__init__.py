from django.contrib import admin

# common
from ..models.common import Address, Person
from .common import PersonAdmin

# accounts
from ..models.accounts import HISAccount, AdministrativeEmployee, Doctor, Nurse, GeneralPersonnel
from .accounts import HISAccountAdmin, EmployeeAdmin, DoctorAdmin, GeneralPersonnelAdmin

# objects
from ..models.objects import Department, DepartmentQualifications, Room, Patient
from .objects import PatientAdmin, RoomAdmin

# tasks
from ..models.tasks import Case, Act, TransferOrder, TransportOrder, AnamnesisReport


# common
admin.site.register(Address)
admin.site.register(Person, PersonAdmin)

# accounts
admin.site.register(HISAccount, HISAccountAdmin)
admin.site.register(AdministrativeEmployee, EmployeeAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Nurse, EmployeeAdmin)
admin.site.register(GeneralPersonnel, GeneralPersonnelAdmin)

# objects
admin.site.register(Department)
admin.site.register(DepartmentQualifications)
admin.site.register(Room, RoomAdmin)
admin.site.register(Patient, PatientAdmin)

# tasks
admin.site.register(Case)
admin.site.register(Act)
admin.site.register(TransferOrder)
admin.site.register(TransportOrder)
admin.site.register(AnamnesisReport)
