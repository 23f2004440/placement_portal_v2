from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from models import db, User, Role, StudentProfile, CompanyProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Bad username or password"}), 401

    role = Role.query.get(user.role_id)
    
    # For company, check if approved/active
    if role.name == 'company':
        if not user.company_profile.is_approved:
            if not user.company_profile.is_active:
                return jsonify({"msg": "Registration not approved"}), 403
            return jsonify({"msg": "Company account pending admin approval"}), 403
        if not user.company_profile.is_active:
            return jsonify({"msg": "Company account is blacklisted/deactivated"}), 403
            
    # For student, check if active
    if role.name == 'student':
        if not user.student_profile.is_active:
            return jsonify({"msg": "Student account is blacklisted/deactivated"}), 403

    additional_claims = {"role": role.name}
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    
    return jsonify(access_token=access_token, role=role.name, user_id=user.id), 200

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"msg": "Username already exists"}), 400
        
    student_role = Role.query.filter_by(name='student').first()
    
    new_user = User(
        username=data.get('username'),
        email=data.get('email', data.get('username')), # fallback to username if no email provided
        password_hash=generate_password_hash(data.get('password')),
        role_id=student_role.id
    )
    db.session.add(new_user)
    db.session.commit()
    
    profile = StudentProfile(
        user_id=new_user.id,
        name=data.get('name'),
        branch=data.get('branch'),
        cgpa=float(data.get('cgpa')),
        year=int(data.get('year'))
    )
    db.session.add(profile)
    db.session.commit()
    
    return jsonify({"msg": "Student registered successfully"}), 201

@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"msg": "Username already exists"}), 400
        
    company_role = Role.query.filter_by(name='company').first()
    
    new_user = User(
        username=data.get('username'),
        email=data.get('email', data.get('username')), # fallback to username if no email provided
        password_hash=generate_password_hash(data.get('password')),
        role_id=company_role.id
    )
    db.session.add(new_user)
    db.session.commit()
    
    profile = CompanyProfile(
        user_id=new_user.id,
        company_name=data.get('company_name'),
        hr_contact=data.get('hr_contact', ''),
        website=data.get('website', '')
    )
    db.session.add(profile)
    db.session.commit()
    
    return jsonify({"msg": "Company registered and pending approval"}), 201
