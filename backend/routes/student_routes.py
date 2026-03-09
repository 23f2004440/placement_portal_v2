from flask import Blueprint, jsonify, request
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity
from models import db, User, StudentProfile, PlacementDrive, Application
from utils.cache import cache

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard', methods=['GET'])
@role_required('student')
def get_dashboard():
    user_id = get_jwt_identity()
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    total_apps = Application.query.filter_by(student_id=profile.id).count()
    
    return jsonify({
        "name": profile.name,
        "branch": profile.branch,
        "cgpa": profile.cgpa,
        "year": profile.year,
        "resume_path": profile.resume_path,
        "total_applications": total_apps
    }), 200

@student_bp.route('/drives', methods=['GET'])
@role_required('student')
@cache.cached(timeout=30, key_prefix='student_drives')
def get_approved_drives():
    drives = PlacementDrive.query.filter_by(status='Approved').all()
    result = []
    
    user_id = get_jwt_identity()
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    for d in drives:
        applied = Application.query.filter_by(student_id=profile.id, drive_id=d.id).first() is not None
        eligible = profile.cgpa >= d.eligibility_cgpa and profile.year == d.eligibility_year
            
        result.append({
            "id": d.id,
            "company_name": d.company_profile.company_name,
            "job_title": d.job_title,
            "job_description": d.job_description,
            "eligibility_branch": d.eligibility_branch,
            "eligibility_cgpa": d.eligibility_cgpa,
            "eligibility_year": d.eligibility_year,
            "application_deadline": d.application_deadline.strftime('%Y-%m-%d') if d.application_deadline else "",
            "has_applied": applied,
            "is_eligible": eligible
        })
    return jsonify(result), 200

@student_bp.route('/applications', methods=['POST'])
@role_required('student')
def apply_for_drive():
    user_id = get_jwt_identity()
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    data = request.get_json()
    drive_id = data.get('drive_id')
    
    drive = PlacementDrive.query.get_or_404(drive_id)
    
    if drive.status != 'Approved':
        return jsonify({"msg": "Cannot apply to an unapproved drive"}), 400
        
    if Application.query.filter_by(student_id=profile.id, drive_id=drive.id).first():
        return jsonify({"msg": "Already applied to this drive"}), 400
        
    app = Application(
        student_id=profile.id,
        drive_id=drive.id
    )
    db.session.add(app)
    db.session.commit()
    
    # Send Email Notification
    student_user = User.query.get(user_id)
    if student_user and student_user.email:
        from tasks import send_email_notification
        send_email_notification.delay(
            student_user.email,
            "Application Received",
            f"You have successfully applied for the '{drive.job_title}' position at '{drive.company_profile.company_name}'."
        )
        
    return jsonify({"msg": "Application submitted successfully"}), 201

@student_bp.route('/applications', methods=['GET'])
@role_required('student')
def get_applications():
    user_id = get_jwt_identity()
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    apps = Application.query.filter_by(student_id=profile.id).all()
    result = []
    for app in apps:
        drive = app.placement_drive
        result.append({
            "id": app.id,
            "company_name": drive.company_profile.company_name,
            "job_title": drive.job_title,
            "status": app.status,
            "application_date": app.application_date.strftime('%Y-%m-%d'),
            "interview_datetime": app.interview_datetime.strftime('%Y-%m-%d %H:%M') if app.interview_datetime else None,
            "interview_link": app.interview_link
        })
    return jsonify(result), 200

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'resumes')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@student_bp.route('/upload-resume', methods=['POST'])
@role_required('student')
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"msg": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400
        
    if file and file.filename.endswith('.pdf'):
        user_id = get_jwt_identity()
        profile = StudentProfile.query.filter_by(user_id=user_id).first()
        
        filename = secure_filename(f"{profile.id}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        profile.resume_path = filename
        db.session.commit()
        return jsonify({"msg": "Resume uploaded successfully", "resume": filename}), 200
    return jsonify({"msg": "Invalid file type. Only PDFs allowed."}), 400

@student_bp.route('/view-resume/<filename>', methods=['GET'])
def view_resume(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)


@student_bp.route('/profile', methods=['PUT'])
@role_required('student')
def update_profile():
    user_id = get_jwt_identity()
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    data = request.get_json()
    if 'name' in data: profile.name = data['name']
    if 'branch' in data: profile.branch = data['branch']
    if 'cgpa' in data: profile.cgpa = float(data['cgpa'])
    if 'year' in data: profile.year = int(data['year'])
    
    db.session.commit()
    return jsonify({"msg": "Profile updated successfully"}), 200

from flask import send_from_directory
import os

@student_bp.route('/export', methods=['POST'])
@role_required('student')
def trigger_export():
    from tasks import export_applications_csv
    
    user_id = get_jwt_identity()
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    # Trigger celery task
    task = export_applications_csv.delay(profile.id)
    
    return jsonify({"status": "ACCEPTED", "msg": "Export job started in background.", "task_id": task.id}), 202

@student_bp.route('/export/<task_id>', methods=['GET'])
@role_required('student')
def check_export_status(task_id):
    from celery_worker import celery
    
    res = celery.AsyncResult(task_id)
    if res.state == 'SUCCESS':
        return jsonify({"status": "SUCCESS", "filename": res.result}), 200
    elif res.state == 'FAILURE':
        return jsonify({"status": "FAILURE"}), 500
    return jsonify({"status": res.state}), 200

@student_bp.route('/download/<filename>', methods=['GET'])
def download_export(filename):
    export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
    return send_from_directory(export_dir, filename, as_attachment=True)

@student_bp.route('/notifications', methods=['GET'])
@role_required('student')
def get_notifications():
    user_id = get_jwt_identity()
    from models import Notification
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    result = [{
        "id": n.id,
        "message": n.message,
        "is_read": n.is_read,
        "created_at": n.created_at.strftime('%Y-%m-%d %H:%M')
    } for n in notifications]
    return jsonify(result), 200

@student_bp.route('/notifications/<int:notif_id>/read', methods=['PUT'])
@role_required('student')
def mark_notification_read(notif_id):
    user_id = get_jwt_identity()
    from models import Notification
    notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first_or_404()
    notif.is_read = True
    db.session.commit()
    return jsonify({"msg": "Marked as read"}), 200
