from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# accounts
from ..models.accounts import HISAccount, AdministrativeEmployee, Doctor, Nurse, GeneralPersonnel
from .accounts import HISAccountAdmin, AdministrativeEmployeeAdmin, DoctorAdmin, NurseAdmin, GeneralPersonnelAdmin

# objects
from ..models.objects import Department, DepartmentQualifications, Room, Patient
from .objects import PatientAdmin, RoomAdmin

# tasks
from ..models.tasks import (
    Case,
    TransportOrder,
    TransferOrder,
    TreatmentOrder,
    ExaminationOrder,
    AnamnesisReport,
    DiagnosisReport,
    ExaminationReport,
    TherapyReport,
    FindingsReport,
)

from .tasks import (
    CaseAdmin,
    TransportOrderAdmin,
    TransferOrderAdmin,
    TreatmentOrderAdmin,
    ExaminationOrderAdmin,
    AnamnesisReportAdmin,
    DiagnosisReportAdmin,
    ExaminationReportAdmin,
    TherapyReportAdmin,
    FindingsReportAdmin,
)

admin.site.site_header = _('NaiveHIS')
admin.site.site_title = _('KIS Verwaltung')
admin.site.index_title = _('KIS Verwaltung')

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

admin.site.register(TransportOrder, TransportOrderAdmin)
admin.site.register(TransferOrder, TransferOrderAdmin)
admin.site.register(TreatmentOrder, TreatmentOrderAdmin)
admin.site.register(ExaminationOrder, ExaminationOrderAdmin)

admin.site.register(AnamnesisReport, AnamnesisReportAdmin)
admin.site.register(DiagnosisReport, DiagnosisReportAdmin)
admin.site.register(ExaminationReport, ExaminationReportAdmin)
admin.site.register(TherapyReport, TherapyReportAdmin)
admin.site.register(FindingsReport, FindingsReportAdmin)
