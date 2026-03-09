from flask import Blueprint, jsonify, request, send_file
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity
from models import db, User, CompanyProfile, PlacementDrive, Application, StudentProfile
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

company_bp = Blueprint('company', __name__)

@company_bp.route('/dashboard', methods=['GET'])
@role_required('company')
def get_dashboard():
    user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=user_id).first()
    
    total_drives = PlacementDrive.query.filter_by(company_id=profile.id).count()
    
    drives = PlacementDrive.query.filter_by(company_id=profile.id).all()
    total_applicants = sum([len(d.applications) for d in drives])
    
    return jsonify({
        "company_name": profile.company_name,
        "is_approved": profile.is_approved,
        "total_drives": total_drives,
        "total_applicants": total_applicants
    }), 200

@company_bp.route('/drives', methods=['POST'])
@role_required('company')
def create_drive():
    user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=user_id).first()
    
    if not profile.is_approved:
        return jsonify({"msg": "Wait for admin approval before creating drives"}), 403
        
    data = request.get_json()
    try:
        deadline = datetime.strptime(data.get('application_deadline'), '%Y-%m-%d')
    except ValueError:
        return jsonify({"msg": "Invalid date format, use YYYY-MM-DD"}), 400
        
    drive = PlacementDrive(
        company_id=profile.id,
        job_title=data.get('job_title'),
        job_description=data.get('job_description'),
        eligibility_branch=data.get('eligibility_branch', ''),
        eligibility_cgpa=float(data.get('eligibility_cgpa', 0.0)),
        eligibility_year=int(data.get('eligibility_year', 0)),
        application_deadline=deadline
    )
    db.session.add(drive)
    db.session.commit()
    return jsonify({"msg": "Placement drive created and pending admin approval"}), 201

@company_bp.route('/drives', methods=['GET'])
@role_required('company')
def get_drives():
    user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=user_id).first()
    drives = PlacementDrive.query.filter_by(company_id=profile.id).all()
    
    result = []
    for d in drives:
        result.append({
            "id": d.id,
            "job_title": d.job_title,
            "status": d.status,
            "application_deadline": d.application_deadline.strftime('%Y-%m-%d'),
            "applicant_count": len(d.applications)
        })
    return jsonify(result), 200

@company_bp.route('/drives/<int:drive_id>/applicants', methods=['GET'])
@role_required('company')
def get_applicants(drive_id):
    user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=user_id).first()
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=profile.id).first()
    if not drive:
        return jsonify({"msg": "Drive not found"}), 404
        
    result = []
    for app in drive.applications:
        student = app.student_profile
        result.append({
            "application_id": app.id,
            "student_name": student.name,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "year": student.year,
            "resume_path": student.resume_path,
            "status": app.status,
            "application_date": app.application_date.strftime('%Y-%m-%d'),
            "interview_datetime": app.interview_datetime.strftime('%Y-%m-%d %H:%M') if app.interview_datetime else None,
            "interview_link": app.interview_link
        })
    return jsonify(result), 200

@company_bp.route('/applications/<int:app_id>/schedule', methods=['POST'])
@role_required('company')
def schedule_interview(app_id):
    data = request.get_json()
    user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=user_id).first()
    
    app = Application.query.get_or_404(app_id)
    if app.placement_drive.company_id != profile.id:
        return jsonify({"msg": "Unauthorized"}), 403
        
    try:
        app.interview_datetime = datetime.strptime(data.get('interview_datetime'), '%Y-%m-%dT%H:%M')
        app.interview_link = data.get('interview_link')
        app.status = 'Shortlisted'
        db.session.commit()
        
        
        from tasks import send_email_notification
        student_user = User.query.get(app.student_profile.user_id)
        if hasattr(student_user, 'email') and student_user.email:
            send_email_notification.delay(
                student_user.email,
                "Interview Scheduled",
                f"Your interview for {app.placement_drive.job_title} at {profile.company_name} is scheduled on {app.interview_datetime.strftime('%Y-%m-%d %H:%M')}. Link: {app.interview_link}"
            )
            
        return jsonify({"msg": "Interview scheduled successfully"}), 200
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 400

@company_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@role_required('company')
def update_application_status(app_id):
    data = request.get_json()
    new_status = data.get('status')
    
    user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=user_id).first()
    
    app = Application.query.get_or_404(app_id)
    if app.placement_drive.company_id != profile.id:
        return jsonify({"msg": "Unauthorized"}), 403
        
    app.status = new_status
    db.session.commit()
    
    # Send Email Notification
    student_user = User.query.get(app.student_profile.user_id)
    if student_user and student_user.email:
        from tasks import send_email_notification
        send_email_notification.delay(
            student_user.email,
            "Application Status Update",
            f"Your application for '{app.placement_drive.job_title}' at '{profile.company_name}' has been updated to: {new_status}."
        )
        
    return jsonify({"msg": f"Application status updated to {new_status}"}), 200

@company_bp.route('/applications/<int:app_id>/offer-letter', methods=['GET'])
@role_required('company')
def generate_offer_letter(app_id):
    user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=user_id).first()
    
    app = Application.query.get_or_404(app_id)
    if app.placement_drive.company_id != profile.id:
        return jsonify({"msg": "Unauthorized"}), 403
        
    if app.status != 'Selected':
        return jsonify({"msg": "Can only generate offer letters for selected candidates"}), 400
        
    student = app.student_profile
    drive = app.placement_drive
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 750, f"OFFER OF EMPLOYMENT: {profile.company_name.upper()}")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 710, f"Date: {datetime.now().strftime('%B %d, %Y')}")
    p.drawString(100, 680, f"Dear {student.name},")
    p.drawString(100, 650, f"We are thrilled to offer you the position of {drive.job_title} at {profile.company_name}.")
    p.drawString(100, 630, "Your impressive background and interview performance made you a standout candidate.")
    p.drawString(100, 600, "Details of the Offer:")
    p.drawString(120, 580, f"- Role: {drive.job_title}")
    p.drawString(120, 560, f"- Company: {profile.company_name}")
    p.drawString(120, 540, "- Type: Full-Time / Permanent")
    
    p.drawString(100, 500, "Please review this dummy offer letter as part of the Placement Portal documentation.")
    p.drawString(100, 480, "Congratulations again on your selection.")
    
    p.drawString(100, 430, "Sincerely,")
    p.drawString(100, 410, f"The HR Team at {profile.company_name}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    filename = f"Offer_Letter_{student.name.replace(' ', '_')}_{drive.job_title.replace(' ', '_')}.pdf"
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )
