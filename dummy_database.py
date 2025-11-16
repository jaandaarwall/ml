from backend.Sqldatabase import db
from backend.models import *
from backend.user_datastore import user_datastore
from flask_security import utils
from datetime import datetime, timedelta, time
from app import create_app

app, _ = create_app()


def seed_dummy_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # --------------------------
        # ROLES
        # --------------------------
        admin_role = user_datastore.find_or_create_role(name='admin')
        doctor_role = user_datastore.find_or_create_role(name='doctor')
        user_role = user_datastore.find_or_create_role(name='user')

        db.session.commit()

        # --------------------------
        # ADMIN USER
        # --------------------------
        if not user_datastore.find_user(email="admin@hospital.com"):
            admin = user_datastore.create_user(
                username="admin",
                email="admin@hospital.com",
                password=utils.hash_password("admin123"),
                roles=[admin_role, doctor_role, user_role],
                phone="9999999999",
                blood_group="O+",
            )
            db.session.add(admin)
            db.session.commit()

        # --------------------------
        # DEPARTMENTS
        # --------------------------
        department_names = [
            ("Cardiology", "Heart & vessels"),
            ("Neurology", "Brain & nerves"),
            ("Orthopedics", "Bones & joints"),
            ("Dermatology", "Skin & hair"),
        ]

        departments = []
        for name, desc in department_names:
            dept = Department(name=name, description=desc)
            db.session.add(dept)
            departments.append(dept)

        db.session.commit()

        # --------------------------
        # DOCTORS + USERS
        # --------------------------
        doctors = []
        for i in range(1, 4):
            user = user_datastore.create_user(
                username=f"doctor{i}",
                email=f"doctor{i}@mail.com",
                password=utils.hash_password("pass123"),
                roles=[doctor_role, user_role],
                phone=f"88888888{i}",
                blood_group="A+",
            )
            db.session.add(user)
            db.session.commit()

            doctor = Doctor(
                user_id=user.id,
                department_id=departments[i % len(departments)].id,
                qualification="MBBS, MD",
                experience_years=5 + i
            )
            db.session.add(doctor)
            doctors.append(doctor)

        db.session.commit()

        # --------------------------
        # PATIENTS + USERS
        # --------------------------
        patients = []
        for i in range(1, 4):
            user = user_datastore.create_user(
                username=f"patient{i}",
                email=f"patient{i}@mail.com",
                password=utils.hash_password("pass123"),
                roles=[user_role],
                phone=f"77777777{i}",
                gender="Male" if i % 2 else "Female",
                blood_group="B+",
                address="Test Address",
            )
            db.session.add(user)
            db.session.commit()

            patient = Patient(user_id=user.id)
            db.session.add(patient)
            patients.append(patient)

        db.session.commit()

        # --------------------------
        # AVAILABILITY FOR DOCTORS
        # --------------------------
        availabilities = []
        for doc in doctors:
            for d in range(3):
                date = datetime.now().date() + timedelta(days=d)
                avail = DoctorAvailability(
                    doctor_id=doc.id,
                    date=date,
                    start_time=time(9, 0),
                    end_time=time(12, 0),
                    total_seats=5,
                    is_available=True
                )
                db.session.add(avail)
                availabilities.append(avail)

        db.session.commit()

        # --------------------------
        # APPOINTMENTS + TREATMENTS
        # --------------------------
        for i, patient in enumerate(patients):
            doctor = doctors[i % len(doctors)]
            date = datetime.now().date()

            # Booked appointment
            apt1 = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                appointment_date=date,
                appointment_time=time(10, 0),
                status="Booked",
                reason="Regular Checkup"
            )
            db.session.add(apt1)

            # Completed appointment + treatment
            apt2 = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                appointment_date=date - timedelta(days=2),
                appointment_time=time(11, 0),
                status="Completed",
                reason="Follow-up"
            )
            db.session.add(apt2)
            db.session.commit()

            treatment = Treatment(
                appointment_id=apt2.id,
                diagnosis="Sample diagnosis",
                prescription="Paracetamol 500mg",
                notes="All good",
                follow_up_required=False
            )
            db.session.add(treatment)

        db.session.commit()

        print("Dummy database successfully populated!")


if __name__ == "__main__":
    seed_dummy_db()
