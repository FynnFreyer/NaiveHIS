from pathlib import Path
from typing import List, Dict

from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from model import *
from utils import encrypt_password


session: Session = None


def connect(db_name, verbose):
    # Singleton DB Connection
    global session
    if session is not None:
        return session

    in_memory = db_name == ':memory:'

    dir_path = Path(__file__).resolve().parent
    db_path = dir_path / db_name if not in_memory else db_name
    is_setup = db_path.exists() if not in_memory else False

    engine: Engine = create_engine('sqlite:///' + str(db_path), echo=verbose, future=True)

    if not is_setup:
        with engine.begin() as connection:
            mapper_registry.metadata.create_all(connection)

    Sess = sessionmaker(bind=engine, future=True)
    session = Sess()

    if not is_setup:
        populate(session)

    return session


def populate(session: Session):
    # Roles
    admin = Role(role_id=1, role=RoleEnum('ADMIN'))
    admissions = Role(role_id=2, role=RoleEnum('ADMISSIONS'))
    pathologist = Role(role_id=3, role=RoleEnum('PATHOLOGIST'))
    radiologist = Role(role_id=4, role=RoleEnum('RADIOLOGIST'))
    surgeon = Role(role_id=5, role=RoleEnum('SURGEON'))

    roles = [admin, admissions, pathologist, radiologist, surgeon]
    session.add_all(roles)

    # Doctors
    salt, pw_hash = encrypt_password('test')
    tom = Doctor(username='tom', first_name='Tom', last_name='Bisson', salt=salt, pw_hash=pw_hash)

    salt, pw_hash = encrypt_password('pass')  # natürlich sollte jedes passwort eigentlich separat gesalted werden
    ghouse = Doctor(username='ghouse', first_name='Gregory', last_name='House', salt=salt, pw_hash=pw_hash)
    mbailey = Doctor(username='mbailey', first_name='Miranda', last_name='Bailey', salt=salt, pw_hash=pw_hash)
    jdorian = Doctor(username='jdorian', first_name='JD', last_name='Dorian', salt=salt, pw_hash=pw_hash)
    shansen = Doctor(username='shansen', first_name='Sydney', last_name='Hansen', salt=salt, pw_hash=pw_hash)

    doctors = [tom, ghouse, mbailey, jdorian, shansen]
    session.add_all(doctors)
    session.commit()  # flush doctors, so they get a doctor_id

    # Doctors Roles
    session.add_all([
        DoctorRole(doctor_id=tom.doctor_id, role_id=admin.role_id),
        DoctorRole(doctor_id=ghouse.doctor_id, role_id=admissions.role_id),
        DoctorRole(doctor_id=ghouse.doctor_id, role_id=radiologist.role_id),
        DoctorRole(doctor_id=mbailey.doctor_id, role_id=surgeon.role_id),
        DoctorRole(doctor_id=mbailey.doctor_id, role_id=radiologist.role_id),
        DoctorRole(doctor_id=jdorian.doctor_id, role_id=surgeon.role_id),
        DoctorRole(doctor_id=jdorian.doctor_id, role_id=pathologist.role_id),
        DoctorRole(doctor_id=shansen.doctor_id, role_id=radiologist.role_id),
        DoctorRole(doctor_id=shansen.doctor_id, role_id=pathologist.role_id)
    ])
    # session.commit()

    # Patients
    rbg = Patient(first_name='Ruth', last_name='Bader-Ginsburg', date_of_birth=date.fromisoformat('1933-03-15'))
    bohlen = Patient(first_name='Dieter', last_name='Bohlen', date_of_birth=date.fromisoformat('1954-02-07'))
    van_gogh = Patient(first_name='Vincent', last_name='Van-Gogh', date_of_birth=date.fromisoformat('1933-03-15'))

    patients = [rbg, bohlen, van_gogh]
    session.add_all(patients)
    session.commit()  # flush patients, so they get a patient_id

    # Cases
    pancreatic_cancer = Case(patient_id=rbg.patient_id)
    penis_fracture = Case(patient_id=bohlen.patient_id)
    cut_ear = Case(patient_id=van_gogh.patient_id)

    cases = [pancreatic_cancer, penis_fracture, cut_ear]
    session.add_all(cases)
    # session.commit()
    
    # Doctors Cases
    session.add_all([
        DoctorCase(doctor_id=ghouse.doctor_id, case_id=penis_fracture.case_id),
        DoctorCase(doctor_id=shansen.doctor_id, case_id=pancreatic_cancer.case_id),
        DoctorCase(doctor_id=jdorian.doctor_id, case_id=pancreatic_cancer.case_id),
        DoctorCase(doctor_id=jdorian.doctor_id, case_id=cut_ear.case_id),
        DoctorCase(doctor_id=mbailey.doctor_id, case_id=cut_ear.case_id),
    ])
    # session.commit()

    # Reports
    from pydicom.dataset import Dataset

    ct_bohlen_text = 'ct shows fracture of the glans penis, operation is recommended'
    ct_bohlen = RadiologyReport(case_id=penis_fracture.case_id, doctor_id=ghouse.doctor_id,
                                text=ct_bohlen_text)

    ct_bohlen_data = Dataset()
    ct_bohlen_data.PatientID = bohlen.patient_id
    ct_bohlen_data.PatientName = bohlen.first_name + ' ' + bohlen.last_name
    ct_bohlen.save_data(ct_bohlen_data)

    tissue_rbg_text = 'advanced stage pancreatic cancer'
    tissue_rbg = PathologyReport(case_id=pancreatic_cancer.case_id, doctor_id=shansen.doctor_id,
                                 text=tissue_rbg_text)

    tissue_rbg_data = Staging.from_string('TisN3M1')
    tissue_rbg.save_data(tissue_rbg_data)

    ct_rbg_text = 'ct of the pancreas'
    ct_rbg = RadiologyReport(case_id=pancreatic_cancer.case_id, doctor_id=shansen.doctor_id,
                             text=ct_rbg_text)

    ct_rbg_data = Dataset()
    ct_rbg_data.PatientID = rbg.patient_id
    ct_rbg_data.PatientName = rbg.first_name + ' ' + bohlen.last_name
    ct_rbg.save_data(ct_rbg_data)

    surgery_rbg_text = 'took some probes of the relevant tissue'
    surgery_rbg = SurgeryReport(case_id=pancreatic_cancer.case_id, doctor_id=jdorian.doctor_id,
                                text=surgery_rbg_text)

    surgery_rbg_data = ResectionMetaData('Pancreas', date.today())
    surgery_rbg.save_data(surgery_rbg_data)

    report_vg_text = 'patient is stable, but seems confused'
    report_vg = Report(case_id=cut_ear.case_id, doctor_id=jdorian.doctor_id,
                       text=report_vg_text)

    reports = [ct_bohlen, tissue_rbg, ct_rbg, surgery_rbg, report_vg]
    session.add_all(reports)

    session.commit()
