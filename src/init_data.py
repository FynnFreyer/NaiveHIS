from datetime import datetime

from NaiveHIS.models.accounts import (
    AdministrativeEmployee,
    Doctor,
    DoctorQualification,
    Nurse,
    GeneralPersonnel,
)

from NaiveHIS.models.objects import (
    Department,
    Patient,
    Room,
)

from NaiveHIS.models.tasks import (
    Case,
    Act,
    TransportOrder,
    TransferOrder,
    Report,
    AnamnesisReport,
)


def save_objs(objs):
    for obj in objs:
        obj.save()


def init_data():
    van_gogh = Patient(
        date_of_birth=datetime.fromisoformat('1853-03-30'),
        first_name='Vincent',
        last_name='van Gogh',
        city='Zundert',
        street='Markt',
        street_number=29,
        zip_code='4880',
        gender='m',
    )

    bohlen = Patient(
        date_of_birth=datetime.fromisoformat('1954-02-07'),
        first_name='Dieter',
        last_name='Bohlen',
        gender='m',
    )

    rbg = Patient(
        title='Dr. jur.',
        first_name='Ruth',
        last_name='Bader-Ginsburg',
        gender='f',
    )

    patients = [van_gogh, bohlen, rbg]
    save_objs(patients)

    admissions = Department(name='Aufnahme')
    intensive_care = Department(name='Intensiv')
    internal_medicine = Department(name='Innere Medizin')
    ops = Department(name='Operations')
    administration = Department(name='Verwaltung')

    departments = [admissions, intensive_care, internal_medicine, ops, administration]
    save_objs(departments)

    admissions_hall = Room(
        name='Aufnahmehalle',
        department=admissions,
        capacity=30,
    )

    op1 = Room(
        name='OP-Raum 1',
        department=intensive_care,
        capacity=1,
    )

    op2 = Room(
        name='OP-Raum 2',
        department=intensive_care,
        capacity=1,
    )

    internal1 = Room(
        name='Raum 1 - Internistische Station',
        department=internal_medicine,
        capacity=4,
    )

    internal2 = Room(
        name='Raum 2 - Internistische Station',
        department=internal_medicine,
        capacity=4,
    )

    break_room = Room(
        name='Pausenraum',
        department=ops,
        capacity=10,
    )

    office = Room(
        name='Büro',
        department=administration,
        capacity=4,
    )

    rooms = [admissions_hall, op1, op2, internal1, internal2, break_room, office]
    save_objs(rooms)

    default_address = {
        'city': 'Berlin',
        'street': 'Augustenburger Platz',
        'street_number': 1,
        'zip_code': '13353',
    }

    default_dob = datetime.fromisoformat('1891-07-01')

    whitman = Nurse(
        department=admissions,
        rank='helper',
        password='test',
        username='whitman',
        email='whitman@example.com',
        first_name='Walt',
        last_name='Whitman',
        gender='m',
        date_of_birth=default_dob,
        **default_address,
    )

    nightingale = Nurse(
        department=intensive_care,
        rank='lead',
        password='test',
        username='nightingale',
        email='nightingale@example.com',
        first_name='Florence',
        last_name='Nightingale',
        gender='f',
        date_of_birth=default_dob,
        **default_address,
    )

    dunant = Nurse(
        department=intensive_care,
        rank='helper',
        password='test',
        username='dunant',
        email='dunant@example.com',
        first_name='Henry',
        last_name='Dunant',
        gender='m',
        date_of_birth=default_dob,
        **default_address,
    )

    karll = Nurse(
        department=internal_medicine,
        rank='trained',
        password='test',
        username='karll',
        email='karll@example.com',
        first_name='Agnes',
        last_name='Karll',
        gender='f',
        date_of_birth=default_dob,
        **default_address,
    )

    mahoney = Nurse(
        department=internal_medicine,
        rank='trained',
        password='test',
        username='mahoney',
        email='mahoney@example.com',
        first_name='Mary',
        last_name='Mahoney',
        gender='f',
        date_of_birth=default_dob,
        **default_address,
    )

    nurses = [whitman, nightingale, dunant, karll, mahoney]
    save_objs(nurses)


    koch = Doctor(
        department=internal_medicine,
        rank='senior',
        password='test',
        username='koch',
        email='koch@example.com',
        title='Dr.',
        first_name='Robert',
        last_name='Koch',
        gender='m',
        date_of_birth=default_dob,
        **default_address,
    )

    koch_quals = (
        DoctorQualification(doctor=koch, qualification='biochemistry'),
        DoctorQualification(doctor=koch, qualification='pharmacology'),
        DoctorQualification(doctor=koch, qualification='microbiology_virology_and_infection_epidemology'),
    )

    hippocrates = Doctor(
        department=intensive_care,
        rank='chief',
        password='test',
        username='hippocrates',
        email='hippocrates@example.com',
        first_name='Hippocrates',
        last_name='von Kos',
        gender='m',
        date_of_birth=default_dob,
        **default_address,
    )

    hippocrates_quals = (
        DoctorQualification(doctor=hippocrates, qualification='anatomy'),
        DoctorQualification(doctor=hippocrates, qualification='surgery'),
    )

    avicenna = Doctor(
        department=internal_medicine,
        rank='chief',
        password='test',
        username='avicenna',
        email='avicenna@example.com',
        first_name='Abu',
        last_name='ibn Sina',
        gender='m',
        date_of_birth=default_dob,
        **default_address,
    )

    avicenna_quals = (
        DoctorQualification(doctor=avicenna, qualification='inner_medicine'),
        DoctorQualification(doctor=avicenna, qualification='general_practice'),
    )

    bingen = Doctor(
        department=intensive_care,
        rank='senior',
        password='test',
        username='bingen',
        email='bingen@example.com',
        first_name='Hildegard',
        last_name='von Bingen',
        gender='f',
        date_of_birth=default_dob,
        **default_address,
    )

    bingen_quals = (
        DoctorQualification(doctor=bingen, qualification='biochemistry'),
        DoctorQualification(doctor=bingen, qualification='hygiene_and_environmental_medicine'),
    )

    fleming = Doctor(
        department=admissions,
        rank='specialist',
        password='test',
        username='fleming',
        email='fleming@example.com',
        title='Sir',
        first_name='Alexander',
        last_name='Fleming',
        gender='m',
        date_of_birth=default_dob,
        **default_address,
    )

    fleming_quals = (
        DoctorQualification(doctor=fleming, qualification='biochemistry'),
        DoctorQualification(doctor=fleming, qualification='microbiology_virology_and_infection_epidemology'),
    )

    doctors = [
        (koch, koch_quals),
        (hippocrates, hippocrates_quals),
        (avicenna, avicenna_quals),
        (bingen, bingen_quals),
        (fleming, fleming_quals)
    ]

    for doctor, quals in doctors:
        doctor.save()
        for qual in quals:
            qual.save()

    hurtig = GeneralPersonnel(
        department=ops,
        function='transport',
        rank='employee',
        password='test',
        username='hurtig',
        email='hurtig@example.com',
        first_name='Harald',
        last_name='Hurtig',
        gender='m',
        date_of_birth=default_dob,
        **default_address,
    )

    schnell = GeneralPersonnel(
        department=ops,
        function='transport',
        rank='employee',
        password='test',
        username='schnell',
        email='schnell@example.com',
        first_name='Sandra',
        last_name='Schnell',
        gender='f',
        date_of_birth=default_dob,
        **default_address,
    )

    transport = [hurtig, schnell]
    save_objs(transport)

    gecko = AdministrativeEmployee(
        department=administration,
        rank='ceo',
        password='test',
        username='gecko',
        email='gecko@example.com',
        first_name='Gordon',
        last_name='Gecko',
        gender='m',
        date_of_birth=default_dob,
        **default_address,
    )

    durstig = AdministrativeEmployee(
        department=administration,
        rank='employee',
        password='test',
        username='durstig',
        email='durstig@example.com',
        first_name='Dietmar',
        last_name='Durstig',
        gender='m',
        date_of_birth=default_dob,
        **default_address,
    )

    administrators = [gecko, durstig]
    save_objs(administrators)

    case_rbg = Case(
        patient=rbg,
        assigned_department=admissions,
    )

    case_rbg.save()

    act_rbg = Act(
        regarding=case_rbg,
        initiator=whitman,
        requesting_department=admissions,
        executing_department=internal_medicine,
    )

    act_rbg.save()

    transport_rbg_internal = TransportOrder(
        issued_by=whitman,
        assigned_to=hurtig,
        assigned_at=datetime.now(),
        regarding=act_rbg,
        from_room=admissions_hall,
        to_room=internal1,
        requested_arrival=datetime.now(),
        supervised=False,
        closed_at=datetime.now(),
    )

    transport_rbg_internal.save()

    transport_rbg_intensive = TransportOrder(
        issued_by=avicenna,
        assigned_to=hurtig,
        assigned_at=datetime.now(),
        regarding=act_rbg,
        from_room=internal1,
        to_room=op2,
        requested_arrival=datetime.now(),
        supervised=True,
        supervised_by=avicenna,
    )

    transport_rbg_intensive.save()

    case_bohlen = Case(
        patient=bohlen,
        assigned_department=admissions,
    )
    
    case_bohlen.save()

    act_bohlen = Act(
        regarding=case_bohlen,
        initiator=whitman,
        requesting_department=admissions,
        executing_department=internal_medicine,
    )

    act_bohlen.save()

    transport_bohlen = TransportOrder(
        issued_by=whitman,
        assigned_to=schnell,
        assigned_at=datetime.now(),
        regarding=act_bohlen,
        from_room=admissions_hall,
        to_room=op1,
        requested_arrival=datetime.now(),
        supervised=True,
        supervised_by=bingen,
    )

    transport_bohlen.save()

    case_van_gogh = Case(
        patient=van_gogh,
        assigned_department=admissions
    )

    case_van_gogh.save()
