from typing import Literal

PermType = Literal['view', 'change', 'delete', 'create']

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

DOCTOR_PERMS = (
    'NaiveHIS.add_act',
    'NaiveHIS.change_act',
    'NaiveHIS.view_act',
    'NaiveHIS.view_patient',
    'NaiveHIS.add_transferorder',
    'NaiveHIS.view_transferorder',
    'NaiveHIS.add_case',
    'NaiveHIS.change_case',
    'NaiveHIS.view_case',
    'NaiveHIS.add_anamnesisreport',
    'NaiveHIS.change_anamnesisreport',
    'NaiveHIS.view_anamnesisreport',
    'NaiveHIS.add_transportorder',
    'NaiveHIS.change_transportorder',
    'NaiveHIS.view_transportorder',
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

REPORT_PERMS = (
    'NaiveHIS.view_anamnesisreport',
)

NURSE_PERMS = (
    # tasks and objects
    'NaiveHIS.add_act',
    'NaiveHIS.change_act',
    'NaiveHIS.view_act',
    'NaiveHIS.view_patient',
    'NaiveHIS.change_patient',
    'NaiveHIS.add_transferorder',
    'NaiveHIS.view_transferorder',
    'NaiveHIS.add_case',
    'NaiveHIS.change_case',
    'NaiveHIS.view_case',
    # views
    'NaiveHIS.view_doctor',
    'NaiveHIS.view_nurse',
    'NaiveHIS.view_generalpersonnel',
    'NaiveHIS.view_administrativeemployee',
    'NaiveHIS.view_department',
    'NaiveHIS.view_room',
    'NaiveHIS.view_departmentqualifications',
    'NaiveHIS.view_anamnesisreport',
    'NaiveHIS.view_transportorder',
    'NaiveHIS.view_transferorder',
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
               or act.regarding.assigned_doctor is self):
            return perm_type in ('create', 'change', 'view')
        elif self.department is act.regarding.assigned_department:
            return perm_type == 'view'
        else:
            return False

    def has_order_perm(self: 'Employee', perm, order: 'Order'):
        ...
