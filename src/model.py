import dataclasses

import json
import enum
import re

from datetime import datetime, date
from typing import List, Dict, Optional, Union
from pydicom import Dataset

from sqlalchemy.orm import registry, declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum, LargeBinary

mapper_registry = registry()
Base = declarative_base()


@mapper_registry.mapped
class Patient:
    __tablename__ = 'patients'

    patient_id: int = Column(Integer, primary_key=True)
    last_name: str = Column(String(30), nullable=False)
    first_name: str = Column(String(30), nullable=False)
    date_of_birth: Optional[date] = Column(Date)
    created: datetime = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated: datetime = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)

    cases = relationship('Case', back_populates='patient')  # type: List[Case]

    def __repr__(self):
        return f'<Patient #{self.patient_id} {self.first_name} {self.last_name}>'

    def __str__(self):
        return f'Patient #{self.patient_id} {self.first_name} {self.last_name}, born on {self.date_of_birth}'


class RoleEnum(enum.Enum):
    ADMIN = 'ADMIN'
    ADMISSIONS = 'ADMISSIONS'
    PATHOLOGIST = 'PATHOLOGIST'
    RADIOLOGIST = 'RADIOLOGIST'
    SURGEON = 'SURGEON'


@mapper_registry.mapped
class Role:
    __tablename__ = 'roles'

    role_id: int = Column(Integer, ForeignKey('doctors.doctor_id'), primary_key=True)
    role: RoleEnum = Column(Enum(RoleEnum), unique=True)
    created: datetime = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated: datetime = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)

    doctors = relationship('DoctorRole', back_populates='role')  # type: List[Doctor]

    def __repr__(self):
        return f'<Role {str(self.role)}>'

    def __str__(self):
        return str(self.role)


@mapper_registry.mapped
class DoctorRole:
    __tablename__ = 'doctors_roles'

    doctor_id: int = Column(Integer, ForeignKey('doctors.doctor_id'), primary_key=True)
    role_id: int = Column(Integer, ForeignKey('roles.role_id'), primary_key=True)
    created: datetime = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated: datetime = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)

    doctor = relationship('Doctor', back_populates='roles')
    role = relationship('Role', back_populates='doctors')

    def __repr__(self):
        return f'<DoctorRole Dr. {self.doctor.first_name} {self.doctor.last_name} is {str(self.role)}>'

    def __str__(self):
        return f'Dr. {self.doctor.first_name} {self.doctor.last_name} is {str(self.role)}'


@mapper_registry.mapped
class Doctor:
    __tablename__ = 'doctors'

    doctor_id: int = Column(Integer, primary_key=True)
    username: str = Column(String(30), nullable=True, unique=True)
    last_name: str = Column(String(30), nullable=False)
    first_name: str = Column(String(30), nullable=False)
    salt: str = Column(LargeBinary(length=64), nullable=False)
    pw_hash: str = Column(LargeBinary(length=128), nullable=False)
    created: datetime = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated: datetime = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)

    roles: List[Role] = relationship('DoctorRole', back_populates='doctor')
    cases = relationship('DoctorCase', back_populates='doctor')  # type: List[Case]
    reports = relationship('Report', back_populates='doctor')  # type: List[Report]

    def __repr__(self):
        return f'<Doctor #{self.doctor_id} {self.first_name} {self.last_name}>'

    def __str__(self):
        return f'Dr. {self.first_name} {self.last_name}'


@mapper_registry.mapped
class DoctorCase:
    __tablename__ = 'doctors_cases'

    doctor_id: int = Column(Integer, ForeignKey('doctors.doctor_id'), primary_key=True)
    case_id: int = Column(Integer, ForeignKey('cases.case_id'), primary_key=True)
    created: datetime = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated: datetime = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)

    doctor: Doctor = relationship('Doctor', back_populates='cases')
    case = relationship('Case', back_populates='doctors')  # type: Case

    def __repr__(self):
        return f'<DoctorCase {self.doctor.first_name} {self.doctor.last_name}>'

    def __str__(self):
        assigned = f'{self.created.year:04d}-{self.created.month:02d}-{self.created.day:02d} ' \
                   f'{self.created.hour:02d}:{self.created.minute:02d}'

        return f'Dr. {self.doctor.first_name} {self.doctor.last_name} was assigned to case #{self.case.case_id} on ' \
               f'{assigned}'


class ReportType(enum.Enum):
    REPORT = 'REPORT'
    RADIOLOGY = 'RADIOLOGY'
    PATHOLOGY = 'PATHOLOGY'
    SURGERY = 'SURGERY'


@mapper_registry.mapped
class Report:
    __tablename__ = 'reports'

    report_id: int = Column(Integer, primary_key=True)
    case_id: int = Column(Integer, ForeignKey('cases.case_id'))
    doctor_id: int = Column(Integer, ForeignKey('doctors.doctor_id'))
    text: str = Column(Text, nullable=False)
    data: str = Column(Text)
    report_type: ReportType = Column(Enum(ReportType), default=ReportType.REPORT)
    created: datetime = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated: datetime = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)

    case = relationship('Case', back_populates='reports')  # type: Case
    doctor: Doctor = relationship('Doctor', back_populates='reports')

    def __repr__(self):
        return f'<Report #{self.report_id} by {self.doctor.first_name} {self.doctor.last_name}>'

    def __str__(self):
        written = f'{self.created.year:04d}-{self.created.month:02d}-{self.created.day:02d} ' \
                  f'{self.created.hour:02d}:{self.created.minute:02d}'
        return f'{self.report_type.value} #{self.case_id} written on {written} ' \
               f'by Dr. {self.doctor.first_name} {self.doctor.last_name}\n' \
               f'Concerning {self.case.patient}\n\n' \
               f'{self.text}\n\n' \
               f'{f"contains additional data, call with the correct type to display" if self.data else ""}'

    def save_data(self, data):
        self.data = data

    def load_data(self):
        return self.data


@mapper_registry.mapped
class RadiologyReport(Report):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report_type = ReportType.RADIOLOGY

    def save_data(self, data: Dataset):
        self.data = data.to_json()

    def load_data(self) -> Dataset:
        return Dataset() if self.data is None else Dataset.from_json(self.data)

    def __repr__(self):
        return f'<RadiologyReport #{self.report_id} by {self.doctor.first_name} {self.doctor.last_name}>'

    def __str__(self):
        return ''.join(super().__str__().splitlines(keepends=True)[:-1]) + '\n' + str(self.load_data())


class Tumor(enum.Enum):
    TX = 'TX'
    T0 = 'T0'
    Tis = 'Tis'
    T1 = 'T1'
    T2 = 'T2'
    T3 = 'T3'
    T4 = 'T4'

    def describe(self):
        desc = {'TX': 'primary tumor cannot be assessed',
                'T0': 'no evidence of primary tumor',
                'Tis': 'carcinoma in situ',
                'T1': 'site/tumor specific, generally small',
                'T2': 'site/tumor specific',
                'T3': 'site/tumor specific, generally large',
                'T4': 'site/tumor specific, generally direct extension into adjacent organs/tissues'}
        return desc[self.value]


class Nodes(enum.Enum):
    NX = 'NX'
    N0 = 'N0'
    N1 = 'N1'
    N2 = 'N2'
    N3 = 'N3'

    def describe(self):
        desc = {'NX': 'nodes cannot be assessed',
                'N0': 'no regional nodal metastasis',
                'N1': 'site/tumor specific',
                'N2': 'site/tumor specific',
                'N3': 'site/tumor specific'}
        return desc[self.value]


class Metastases(enum.Enum):
    M0 = 'M0'
    M1 = 'M1'

    def describe(self):
        desc = {'M0': 'no distant metastasis',
                'M1': 'distant metastasis present'}
        return desc[self.value]


# @mapper_registry.mapped
@dataclasses.dataclass
class Staging:
    # __tablename__ = 'stagings'

    # report_id: int = Column(ForeignKey('reports.report_id'), primary_key=True)
    t: Tumor = Column(Enum(Tumor), nullable=False)
    n: Nodes = Column(Enum(Nodes), nullable=False)
    m: Metastases = Column(Enum(Metastases), nullable=False)

    # report = relationship('PathologyReport', back_populates='staging')  # type: PathologyReport
    def __init__(self, t, n, m):
        self.t = t
        self.n = n
        self.m = m

    @staticmethod
    def from_string(string, report=None):
        tnm_regex = re.compile(r'(T\S+)(N\S+)(M\S+)')
        search = tnm_regex.search(string)

        try:
            t = Tumor(search.group(1))
            n = Nodes(search.group(2))
            m = Metastases(search.group(3))
        except AttributeError:
            raise ValueError('Not a valid TNM classification string')

        staging = Staging(t, n, m)  # if report is None \
        # else Staging(report_id=report.report_id, t=t, n=n, m=m)

        return staging

    def to_string(self):
        return self.t.value + self.n.value + self.m.value

    def describe(self):
        return self.t.value + ': ' + self.t.describe() + '\n' + \
               self.n.value + ': ' + self.n.describe() + '\n' + \
               self.m.value + ': ' + self.m.describe() + '\n'

    def __repr__(self):
        return f'<Staging {self.to_string()}>'

    def __str__(self):
        return self.to_string() + '\n' + self.describe()


@mapper_registry.mapped
class PathologyReport(Report):
    # staging: Staging = relationship('Staging', back_populates='report')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report_type = ReportType.PATHOLOGY

    def save_data(self, data: Staging):
        self.data = data.to_string()

    def load_data(self) -> Staging:
        return Staging.from_string(self.data)

    def __repr__(self):
        return f'<PathologyReport #{self.report_id} by {self.doctor.first_name} {self.doctor.last_name}>'

    def __str__(self):
        return ''.join(super().__str__().splitlines(keepends=True)[:-1]) + '\n' + str(self.load_data())


class ResectionMetaData:
    def __init__(self, organ: str, resection_date: date):
        self.organ = organ
        self.resection_date = resection_date

    def to_string(self):
        return self.organ + ';' + self.resection_date.isoformat()

    @staticmethod
    def from_string(string: str):
        data = string.split(';')

        organ = data[0]
        resection_date = date.fromisoformat(data[1])

        return ResectionMetaData(organ, resection_date)

    def __str__(self):
        return f'Tissue from {self.organ} was removed on {self.resection_date}'


@mapper_registry.mapped
class SurgeryReport(Report):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report_type = ReportType.SURGERY

    def save_data(self, data: ResectionMetaData):
        self.data = data.to_string()

    def load_data(self) -> ResectionMetaData:
        return ResectionMetaData.from_string(self.data)

    def __repr__(self):
        return f'<SurgeryReport #{self.report_id} by {self.doctor.first_name} {self.doctor.last_name}>'

    def __str__(self):
        return ''.join(super().__str__().splitlines(keepends=True)[:-1]) + '\n' + str(self.load_data())


@mapper_registry.mapped
class Case:
    __tablename__ = 'cases'

    case_id: int = Column(Integer, primary_key=True)
    patient_id: int = Column(Integer, ForeignKey('patients.patient_id'), nullable=False)
    created: datetime = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated: datetime = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)

    patient: Patient = relationship('Patient', back_populates='cases')
    doctors: List[DoctorCase] = relationship('DoctorCase', back_populates='case')
    reports: List[Report] = relationship('Report', back_populates='case')

    def __repr__(self):
        return f'<Case #{self.case_id} for patient #{self.patient_id}>'

    def __str__(self):
        nl = '\n'
        return f'Case #{self.case_id}\n' \
               f'Concerning {self.patient}\n' \
               f'Participating doctors: {" ".join([str(dc.doctor.username) for dc in self.doctors])}\n' \
               f'#{len(self.reports)} report/s filed: \n{nl.join([repr(report) for report in self.reports])}'
