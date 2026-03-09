from app import create_app
from models import db, Role, User
from werkzeug.security import generate_password_hash

app = create_app()

def init_db():
    with app.app_context():
        db.drop_all()
        
        db.create_all()

        #  Roles
        role_names = ['admin', 'company', 'student']
        for name in role_names:
            if not Role.query.filter_by(name=name).first():
                r = Role(name=name)
                db.session.add(r)
        db.session.commit()

        #  default Admin
        admin_role = Role.query.filter_by(name='admin').first()
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role_id=admin_role.id
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin created (admin / admin123)")
        else:
            print("Admin user already exists")

if __name__ == '__main__':
    init_db()
