from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # 'admin', 'company', 'student'
    users = db.relationship('User', backref='role', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False)
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False)

class CompanyProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(200))
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True) # For deactivation/blacklisting
    
    drives = db.relationship('PlacementDrive', backref='company_profile', lazy=True)

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False) 
    resume_path = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True) # For deactivation/blacklisting
    
    applications = db.relationship('Application', backref='student_profile', lazy=True)

class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profile.id'), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_branch = db.Column(db.String(255)) 
    eligibility_cgpa = db.Column(db.Float, nullable=False)
    eligibility_year = db.Column(db.Integer, nullable=False)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='Pending') # 'Pending', 'Approved', 'Rejected', 'Closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    applications = db.relationship('Application', backref='placement_drive', lazy=True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    ats_score = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='Applied') # 'Applied', 'Shortlisted', 'Selected', 'Rejected'
    interview_datetime = db.Column(db.DateTime)
    interview_link = db.Column(db.String(255))

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
