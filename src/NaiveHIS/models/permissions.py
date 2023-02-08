from typing import Literal

PermType = Literal['view', 'change', 'delete', 'create']

_view_perms = (
    # all model view permissions
    'NaiveHIS.view_act',
    'NaiveHIS.view_department',
    'NaiveHIS.view_patient',
    'NaiveHIS.view_room',
    'NaiveHIS.view_hisaccount',
    'NaiveHIS.view_doctor',
    'NaiveHIS.view_transferorder',
    'NaiveHIS.view_departmentqualifications',
    'NaiveHIS.view_case',
    'NaiveHIS.view_anamnesisreport',
    'NaiveHIS.view_transportorder',
    'NaiveHIS.view_nurse',
    'NaiveHIS.view_generalpersonnel',
    'NaiveHIS.view_doctorqualification',
    'NaiveHIS.view_administrativeemployee',
)

_view_personell_perms = (
    'NaiveHIS.view_nurse',
    'NaiveHIS.view_doctor',
    'NaiveHIS.view_generalpersonnel',
    'NaiveHIS.view_administrativeemployee',
)

ADMINISTRATIVE_EMPLOYEE_PERMS = (
    # objects
    'NaiveHIS.add_department',
    'NaiveHIS.change_department',
    'NaiveHIS.delete_department',
    'NaiveHIS.view_department',
    'NaiveHIS.add_room',
    'NaiveHIS.change_room',
    'NaiveHIS.delete_room',
    'NaiveHIS.view_room',
    # accounts
    'NaiveHIS.add_doctor',
    'NaiveHIS.change_doctor',
    'NaiveHIS.view_doctor',
    'NaiveHIS.add_nurse',
    'NaiveHIS.change_nurse',
    'NaiveHIS.view_nurse',
    'NaiveHIS.add_administrativeemployee',
    'NaiveHIS.change_administrativeemployee',
    'NaiveHIS.view_administrativeemployee',
    'NaiveHIS.add_generalpersonnel',
    'NaiveHIS.change_generalpersonnel',
    'NaiveHIS.view_generalpersonnel',
    # qualifications
    'NaiveHIS.add_doctorqualification',
    'NaiveHIS.change_doctorqualification',
    'NaiveHIS.delete_doctorqualification',
    'NaiveHIS.view_doctorqualification',
    'NaiveHIS.add_departmentqualifications',
    'NaiveHIS.change_departmentqualifications',
    'NaiveHIS.delete_departmentqualifications',
    'NaiveHIS.view_departmentqualifications',
)

_medical_perms = (
    'NaiveHIS.add_act',
    'NaiveHIS.change_act',
    'NaiveHIS.view_act',
    'NaiveHIS.add_patient',
    'NaiveHIS.change_patient',
    'NaiveHIS.view_patient',
    'NaiveHIS.add_case',
    'NaiveHIS.change_case',
    'NaiveHIS.view_case',
)

_order_perms = (
    'NaiveHIS.view_transportorder',
    'NaiveHIS.add_transportorder',
    'NaiveHIS.view_transferorder',
    'NaiveHIS.add_transferorder',
    'NaiveHIS.change_transferorder',
    'NaiveHIS.view_treatmentorder',
    'NaiveHIS.add_treatmentorder',
    'NaiveHIS.change_treatmentorder',
    'NaiveHIS.view_examinationorder',
    'NaiveHIS.add_examinationorder',
    'NaiveHIS.change_examinationorder',
)

_report_perms = (
    'NaiveHIS.add_anamnesisreport',
    'NaiveHIS.view_anamnesisreport',
    'NaiveHIS.change_anamnesisreport',
    'NaiveHIS.add_diagnosisreport',
    'NaiveHIS.view_diagnosisreport',
    'NaiveHIS.change_diagnosisreport',
    'NaiveHIS.add_examinationreport',
    'NaiveHIS.view_examinationreport',
    'NaiveHIS.change_examinationreport',
    'NaiveHIS.add_therapyreport',
    'NaiveHIS.view_therapyreport',
    'NaiveHIS.change_therapyreport',
    'NaiveHIS.add_findingsreport',
    'NaiveHIS.view_findingsreport',
    'NaiveHIS.change_findingsreport',
)

DOCTOR_PERMS = (
    *_view_perms,
    *_order_perms,
    *_report_perms,
)

NURSE_PERMS = (*DOCTOR_PERMS,)
GENERALPERSONNEL_PERMS = (
    'NaiveHIS.view_transportorder',
    'NaiveHIS.change_transportorder',
    *_view_personell_perms,
)


class EmployeePerms:
    def has_case_perm(self: 'Employee', perm_type: PermType, case: 'Case'):
        if perm_type in ('view', 'change'):
            return self.department is case.assigned_department
        else:
            return False

    def has_employee_perm(self: 'Employee', perm_type: PermType, employee: 'Employee'):
        from .accounts import GeneralPersonnel
        if perm_type == 'view':
            if self.department is employee.department:
                return True
            elif self.role is employee.role:
                return True
            elif employee.role is GeneralPersonnel:
                return True
        else:
            return False

    def has_act_perm(self: 'Employee', perm_type: PermType, act: 'Act'):
        if any(act.initiator is self
               or act.executing_department is self
               or act.case.assigned_doctor is self):
            return perm_type in ('create', 'change', 'view')
        elif self.department is act.case.assigned_department:
            return perm_type == 'view'
        else:
            return False

    def has_order_perm(self: 'Employee', perm, order: 'Order'):
        ...
