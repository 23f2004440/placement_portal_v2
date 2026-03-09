from app import create_app
from models import db, Notification, StudentProfile
app = create_app()
with app.app_context():
    students = StudentProfile.query.all()
    for s in students:
        db.session.add(Notification(user_id=s.user_id, message='Welcome to the Placement Portal! Notifications are now enabled.'))
    db.session.commit()
    print("Injected test notifications.")
