from django.contrib.auth.models import Group


class Doctor(Group):
    ...


class Radiologist(Doctor):
    ...


class Pathologist(Doctor):
    ...


class LabPhysician(Doctor):
    ...


class Surgeon(Doctor):
    ...


class Internist(Doctor):
    ...


class LabTechnician(Group):
    ...


class Transporter(Group):
    ...


class Nurse(Group):
    ...


class Cleaner(Group):
    ...

class Administration(Group):
    ...
