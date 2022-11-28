from getpass import getpass
from utils import encrypt_password, check_password
from model import *

from sqlalchemy import select, delete
from sqlalchemy.orm import Session


def authenticate(session: Session):
    correct = False
    while not correct:
        username = input('HIS login: ')
        password = getpass('Password: ')

        try:
            doctor = session.query(Doctor).filter_by(username=username).one()
            correct = check_password(password, doctor.salt, doctor.pw_hash)
        except Exception as e:
            correct = False

        if not correct:
            print('Login incorrect')

    return doctor


import db
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Start the HIS')

    parser.add_argument('--mem', action='store_true', help='Do not persist data, but open an in memory DB instead')
    parser.add_argument('-v', '--verbose', action='store_true', help='Echo SQL transactions')

    return parser.parse_args()


def print_help():
    print('''
possible commands:

list <entity_type>              - list all entities you have access to
create <entity_type>            - Create entities, e.g. 'create patient'
show <entity_type> <identifier> - show details for entity; identifier must be the id
assign <case_id>                - assign a doctor to a case

possible entity_types:

case
<type>report                   - type ::= [ any | radiology | surgery | pathology ] 
patient


q to quit
    ''')


def answer_bool(msg):
    correct = False
    while not correct:
        answer = input(msg + ' (y/n): ').lower()
        correct = answer in ['y', 'n']
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        print('Not a valid answer: ')


def create_case(session: Session):
    answer = ''
    while answer.lower() not in ['y', 'n']:
        answer = input('Create new Patient? (y/n): ')
    new_patient = answer == 'y'
    if new_patient:
        patient = create_patient(session)
    else:
        found = False
        while not found:
            try:
                # TODO test this path, specifically the string/int comparison w/o parsing
                patient_id = input('Please enter patient id (int) to associate with the case: ')
                stmt = select(Patient).where(Patient.patient_id == patient_id)
                patient = session.execute(stmt).one()[0]
                found = True
            except:
                print(f'Patient with id {patient_id} could not be found.')
    case = Case(patient_id=patient.patient_id)

    session.add(case)
    session.commit()

    return case


def create_patient(session: Session):
    first_name = input('First Name: ')
    last_name = input('Last Name: ')
    correct = False
    date_of_birth = None
    while not correct:
        date_of_birth_string = input('Date of birth in ISO-format (YYYY-MM-DD)\nLeave blank if unknown: ')
        try:
            if date_of_birth_string == '':
                break
            date_of_birth = date.fromisoformat(date_of_birth_string)
            correct = True
        except ValueError:
            print('Date could not be parsed, please use ISO-format (YYYY-MM-DD), or leave blank.')

    patient = Patient(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth)

    session.add(patient)
    session.commit()

    return patient


def create_report(session: Session, doctor: Doctor, case: Case, report_type: ReportType):
    text = input('Enter report text: ')
    kwargs = {'case_id': case.case_id, 'doctor_id': doctor.doctor_id, 'text': text, 'report_type': report_type}

    if report_type is ReportType.REPORT:
        report = Report(**kwargs)
    elif report_type is ReportType.PATHOLOGY:
        report = PathologyReport(**kwargs)
        answer = answer_bool('Staging necessary?')
        if answer:
            data = create_staging()
            report.save_data(data)
    elif report_type is ReportType.RADIOLOGY:
        report = RadiologyReport(**kwargs)
        answer = answer_bool('Create DICOM-data?')
        if answer:
            data = create_dataset(case)
            report.save_data(data)
    elif report_type is ReportType.SURGERY:
        report = SurgeryReport(**kwargs)
        answer = answer_bool('Tissue extracted?')
        if answer:
            data = create_resection_meta_data()
            report.save_data(data)
    else:
        raise NotImplementedError('Passed unknown ReportType')

    session.add(report)
    session.commit()

    return report


def create_dataset(case: Case):
    patient_id = case.patient.patient_id
    patient_name = case.patient.first_name + ' ' + case.patient.last_name

    ds = Dataset()

    ds.PatientID = patient_id
    ds.PatientName = patient_name

    return ds


def create_resection_meta_data():
    organ = input('Organ from which tissue was extracted: ')
    date_of_resection = date.today()
    correct = False
    while not correct:
        date_of_resection_string = input('Date of resection in ISO-format (YYYY-MM-DD)\nLeave blank for today: ')
        try:
            if date_of_resection_string == '':
                break
            date_of_resection = date.fromisoformat(date_of_resection_string)
            correct = True
        except ValueError:
            print('Date could not be parsed, please use ISO-format (YYYY-MM-DD), or leave blank.')

    return ResectionMetaData(organ, date_of_resection)


def create_staging():
    correct = False
    while not correct:
        tnm_string = input('Please enter valid TNM string (case sensitive): ')
        try:
            staging = Staging.from_string(tnm_string)
            correct = True
        except ValueError:
            print('Not a valid TNM classification')
    return staging


# stmt = select(RadiologyReport).where(RadiologyReport.report_type == ReportType.RADIOLOGY)
# result = session.execute(stmt).scalars()
# print([rep for rep in result])


def is_privileged(doctor: Doctor):
    role_ids = [dr.role_id for dr in doctor.roles]
    stmt = select(Role.role).where(Role.role_id.in_(role_ids))
    roles = list(session.execute(stmt).scalars())
    privileged = any([role == RoleEnum.ADMIN or role == RoleEnum.ADMISSIONS for role in roles])
    return privileged


if __name__ == '__main__':
    args = parse_args()

    if args.mem:
        db_name = ':memory:'
    else:
        db_name = 'db.sqlite'

    if args.verbose:
        verbose = True
    else:
        verbose = False

    session = db.connect(db_name, verbose)
    try:
        with session:
            doctor = authenticate(session)
            privileged = is_privileged(doctor)

            commands = ['list', 'create', 'show', 'assign']
            entity_types = ['case', 'patient', 'report', 'anyreport', 'radiologyreport', 'surgeryreport',
                            'pathologyreport']

            running = True
            while running:
                visible_case_ids = [case.case_id for case in doctor.cases]
                visible_report_ids = [report.report_id for report in doctor.reports] + \
                                     [report.report_id for doctor_case in doctor.cases
                                      for report in doctor_case.case.reports]
                visible_patient_ids = [doctor_case.case.patient_id for doctor_case in doctor.cases]

                cmd = input('> ')
                tokens = cmd.split()
                if tokens[0] == 'q':
                    running = False
                elif tokens[0] == '?':
                    print_help()
                else:
                    processing_cmd = True
                    while processing_cmd:
                        if tokens[0] not in commands:
                            print(f'command not found: {tokens[0]}')
                            print_help()
                            break
                        cmd = tokens[0]
                        if cmd == 'list':
                            if len(tokens) < 2 or not tokens[1] in entity_types:
                                print(f'missing valid entity type: {" ".join(tokens)}')
                                print_help()
                                break

                            entity_type = tokens[1]

                            if entity_type == 'case':
                                stmt = select(Case)
                                if not privileged:
                                    stmt = stmt.where(Case.case_id.in_(visible_case_ids))
                            elif entity_type == 'patient':
                                stmt = select(Patient)
                                if not privileged:
                                    stmt = stmt.where(Patient.patient_id.in_(visible_patient_ids))
                            elif 'report' in entity_type:
                                if entity_type.startswith('pathology'):
                                    stmt = select(PathologyReport).where(
                                        PathologyReport.report_type == ReportType.PATHOLOGY)
                                elif entity_type.startswith('radiology'):
                                    stmt = select(RadiologyReport).where(
                                        RadiologyReport.report_type == ReportType.RADIOLOGY)
                                elif entity_type.startswith('surgery'):
                                    stmt = select(SurgeryReport).where(SurgeryReport.report_type == ReportType.SURGERY)
                                elif entity_type.startswith('any'):
                                    stmt = select(Report)
                                else:
                                    stmt = select(Report).where(Report.report_type == ReportType.REPORT)
                                if not privileged:
                                    stmt = stmt.where(Report.report_id.in_(visible_report_ids))
                            result = list(session.execute(stmt).scalars())
                            nl = '\n'
                            print(f'# of records: {len(result)} '
                                  f'{nl + "maybe try entity_type anyreport" if "report" in entity_type and len(result) == 0 else ""}')
                            for record in result:
                                print(repr(record))
                            break
                        elif cmd == 'create':
                            # Todo nasty duplication
                            if len(tokens) < 2 or not tokens[1] in entity_types:
                                print(f'missing valid entity type: {" ".join(tokens)}')
                                print_help()
                                break

                            entity_type = tokens[1]
                            if entity_type == 'case':
                                if not privileged:
                                    print("You don't have sufficient rights to do this.")
                                    break
                                case = create_case(session)
                                print(f'Successfully created {repr(case)}')
                                break
                            elif entity_type == 'patient':
                                if not privileged:
                                    print("You don't have sufficient rights to do this.")
                                    break
                                patient = create_patient(session)
                                print(f'Successfully created {repr(patient)}')
                                break
                            elif 'report' in entity_type:
                                available_report_type = True
                                if entity_type.startswith('pathology'):
                                    report_type = ReportType.PATHOLOGY
                                    if RoleEnum.PATHOLOGIST not in [dr.role.role for dr in doctor.roles]:
                                        available_report_type = False
                                elif entity_type.startswith('radiology'):
                                    report_type = ReportType.RADIOLOGY
                                    if RoleEnum.RADIOLOGIST not in [dr.role.role for dr in doctor.roles]:
                                        available_report_type = False
                                elif entity_type.startswith('surgery'):
                                    report_type = ReportType.SURGERY
                                    if RoleEnum.SURGEON not in [dr.role.role for dr in doctor.roles]:
                                        available_report_type = False
                                elif entity_type.startswith('any'):
                                    report_type = ReportType.REPORT
                                else:
                                    report_type = ReportType.REPORT

                                if not available_report_type:
                                    print('You cannot create reports outside of your roles: ')
                                    for role in [dr.role.role for dr in doctor.roles]:
                                        print(role.value.title())
                                    break

                                print('Your cases are: ')
                                if not privileged:
                                    for case in doctor.cases:
                                        print(repr(case.case))
                                else:
                                    all_cases = session.execute(select(Case)).scalars()
                                    for case in all_cases:
                                        print(repr(case))

                                correct = False
                                while not correct:
                                    case_id = input('Enter id of case you are reporting on: ')
                                    try:
                                        case_id = int(case_id)
                                        correct = True
                                    except ValueError:
                                        correct = False

                                if not privileged and case_id not in visible_case_ids:
                                    print("You don't have sufficient rights to do this.")
                                    break

                                stmt = select(Case).where(Case.case_id == case_id)
                                case = session.execute(stmt).one()[0]

                                report = create_report(session, doctor, case, report_type)
                                print(f'Successfully created {repr(report)}')
                                break

                        elif cmd == 'show':
                            # Todo nasty duplication
                            if len(tokens) < 2 or not tokens[1] in entity_types:
                                print(f'missing valid entity type: {" ".join(tokens)}')
                                print_help()
                                break

                            valid_id = False
                            if len(tokens) >= 3:
                                try:
                                    identifier = int(tokens[2])
                                    valid_id = True
                                except ValueError:
                                    valid_id = False

                            if not valid_id:
                                print(f'missing valid identifier: {" ".join(tokens)}')
                                print_help()
                                break

                            entity_type = tokens[1]
                            # duplicate, but makes it more resilient to stupid changes in the gross validation part
                            identifier = int(tokens[2])

                            if entity_type == 'case':
                                if not privileged and identifier not in visible_case_ids:
                                    print("You don't have sufficient rights to do this.")
                                    break
                                stmt = select(Case).where(Case.case_id == identifier)
                            elif entity_type == 'patient':
                                if not privileged and identifier not in visible_case_ids:
                                    print("You don't have sufficient rights to do this.")
                                    break
                                stmt = select(Patient).where(Patient.patient_id == identifier)
                            elif 'report' in entity_type:
                                if entity_type.startswith('pathology'):
                                    stmt = select(PathologyReport).where(
                                        PathologyReport.report_type == ReportType.PATHOLOGY)
                                elif entity_type.startswith('radiology'):
                                    stmt = select(RadiologyReport).where(
                                        RadiologyReport.report_type == ReportType.RADIOLOGY)
                                elif entity_type.startswith('surgery'):
                                    stmt = select(SurgeryReport).where(SurgeryReport.report_type == ReportType.SURGERY)
                                elif entity_type.startswith('any'):
                                    stmt = select(Report)
                                else:
                                    stmt = select(Report).where(Report.report_type == ReportType.REPORT)
                                stmt = stmt.where(Report.report_id == identifier)

                            try:
                                record = session.execute(stmt).one()[0]
                            except:
                                if 'report' in entity_type:
                                    print('Not found a Report with this id, have you chosen the right report type?\n'
                                          'Alternatively try the anyreport type')
                                break

                            print(repr(record))
                            print(record)

                            if entity_type == 'patient' and privileged:
                                print('Medical history: ')
                                patient = record
                                cases_stmt = select(Case).where(Case.patient_id == patient.patient_id)
                                cases = session.execute(cases_stmt).scalars()
                                for case in cases:
                                    print(case)
                                    doctors_cases_statement = select(DoctorCase).where(
                                        DoctorCase.case_id == case.case_id)
                                    doctors_cases = session.execute(doctors_cases_statement).scalars()
                                    for doctor_case in doctors_cases:
                                        print('\t', doctor_case)

                            break
                        elif cmd == 'assign':
                            valid_id = False
                            if len(tokens) >= 2:
                                try:
                                    case_id = int(tokens[1])
                                    case = session.execute(select(Case).where(Case.case_id == case_id)).one()[0]
                                    valid_id = True
                                except ValueError:
                                    print('Please supply a valid integer for the case id')
                                    valid_id = False
                                except:
                                    print(f'Could not find case with id {case_id}')
                                    valid_id = False

                            if not valid_id:
                                print(f'missing valid identifier: {" ".join(tokens)}')
                                print_help()
                                break

                            if not privileged:
                                print("You don't have sufficient rights to do this.")
                                break

                            print('Available doctors:')
                            doctors = session.execute(select(Doctor)).scalars()
                            for doctor in doctors:
                                print(repr(doctor))

                            correct = False
                            while not correct:
                                doctor_id = input('Enter id of doctor to assign the case to: ')
                                try:
                                    doctor_id = int(doctor_id)
                                    doctor = session.execute(select(Doctor).where(Doctor.doctor_id == doctor_id)).one()[
                                        0]
                                    correct = True
                                except ValueError:
                                    print('Please supply a valid integer')
                                    correct = False
                                except:
                                    print(f'Could not find doctor with id {doctor_id}')
                                    correct = False

                                try:
                                    session.execute(select(DoctorCase).
                                                    where(DoctorCase.doctor_id == doctor_id).
                                                    where(DoctorCase.case_id == case_id)).one()
                                    print(f'{doctor} is already assigned to the case!')
                                    already_assigned = True
                                except:
                                    already_assigned = False

                                if already_assigned:
                                    break

                                doctor_case = DoctorCase(doctor_id=doctor_id, case_id=case_id)
                                session.add(doctor_case)
                                session.commit()

                        processing_cmd = False
                        session.commit()

            session.commit()
            session.close()
    except KeyboardInterrupt:
        print()
    except EOFError:
        print()
    print('Good bye!')
    exit(0)
