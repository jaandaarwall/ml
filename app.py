from application import create_app, db, user_datastore
from application.models import User, Roles, Department, Doctor
from flask_security import hash_password
import os

app = create_app()

with app.app_context():
    db.create_all()

    # Create roles
    if not user_datastore.find_role('admin'):
        user_datastore.create_role(name='admin', description='Hospital Administrator')
    if not user_datastore.find_role('doctor'):
        user_datastore.create_role(name='doctor', description='Medical Doctor')
    if not user_datastore.find_role('patient'):
        user_datastore.create_role(name='patient', description='Hospital Patient')
    
    db.session.commit()
    
    # Create admin user
    if not user_datastore.find_user(email='admin@hospital.com'):
        user_datastore.create_user(
            username='admin',
            full_name='System Administrator',
            email='admin@hospital.com',
            password=hash_password('admin123'),
            active=True,
            roles=['admin']
        )
        db.session.commit()

    # Create departments if not exist
    departments_data = [
        {'name': 'Cardiology', 'description': 'Heart and cardiovascular system'},
        {'name': 'Neurology', 'description': 'Brain and nervous system'},
        {'name': 'Orthopedics', 'description': 'Bones and joints'},
        {'name': 'Pediatrics', 'description': 'Child healthcare'},
        {'name': 'Dermatology', 'description': 'Skin conditions'},
        {'name': 'General Medicine', 'description': 'General health issues'}
    ]
    
    for dept_data in departments_data:
        if not Department.query.filter_by(name=dept_data['name']).first():
            dept = Department(**dept_data)
            db.session.add(dept)
    
    db.session.commit()


if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    os.makedirs('frontend/templates', exist_ok=True)
    app.run(debug=True, port=5000)
