from django.contrib import admin

# accounts
from ..models.accounts import HISAccount, Employee, AdministrativeEmployee, Doctor, Nurse, GeneralPersonnel
from .accounts import HISAccountAdmin, AdministrativeEmployeeAdmin, DoctorAdmin, NurseAdmin, GeneralPersonnelAdmin

# objects
from ..models.objects import Department, DepartmentQualifications, Room, Patient
from .objects import PatientAdmin, RoomAdmin

# tasks
from ..models.tasks import Case, Act, TransferOrder, TransportOrder, AnamnesisReport
from .tasks import CaseAdmin, ActAdmin, TransportOrderAdmin  # , TransferOrderAdmin, TransportOrderAdmin, AnamnesisReportAdmin

# accounts
admin.site.register(HISAccount, HISAccountAdmin)
admin.site.register(AdministrativeEmployee, AdministrativeEmployeeAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Nurse, NurseAdmin)
admin.site.register(GeneralPersonnel, GeneralPersonnelAdmin)

# objects
admin.site.register(Department)
admin.site.register(DepartmentQualifications)
admin.site.register(Room, RoomAdmin)
admin.site.register(Patient, PatientAdmin)

# tasks
admin.site.register(Case, CaseAdmin)
admin.site.register(Act, ActAdmin)
admin.site.register(TransferOrder)
admin.site.register(TransportOrder, TransportOrderAdmin)
admin.site.register(AnamnesisReport)
