from flask import Blueprint, jsonify, request, send_file
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity
from models import db, User, CompanyProfile, StudentProfile, PlacementDrive, Application
from utils.cache import cache
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def get_dashboard_stats():
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    total_selected = Application.query.filter_by(status='Selected').count()
    
    return jsonify({
        "total_students": total_students,
        "total_companies": total_companies,
        "total_drives": total_drives,
        "total_applications": total_applications,
        "total_selected": total_selected
    }), 200

@admin_bp.route('/companies', methods=['GET'])
@role_required('admin')
def get_companies():
    companies = CompanyProfile.query.all()
    result = []
    for c in companies:
        result.append({
            "id": c.id,
            "company_name": c.company_name,
            "hr_contact": c.hr_contact,
            "website": c.website,
            "is_approved": c.is_approved,
            "is_active": c.is_active
        })
    return jsonify(result), 200

@admin_bp.route('/companies/<int:company_id>/approve', methods=['POST'])
@role_required('admin')
def approve_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.is_approved = True
    db.session.commit()
    return jsonify({"msg": "Company approved successfully"}), 200

@admin_bp.route('/companies/<int:company_id>/reject', methods=['DELETE'])
@role_required('admin')
def reject_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    if company.is_approved:
        return jsonify({"msg": "Cannot reject an already approved company"}), 400
    
    # Mark as rejected by keeping is_approved=False and setting is_active=False
    company.is_active = False
    db.session.commit()
    return jsonify({"msg": "Company registration rejected and marked as inactive"}), 200

@admin_bp.route('/companies/<int:company_id>/toggle-status', methods=['POST'])
@role_required('admin')
def toggle_company_status(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.is_active = not company.is_active
    db.session.commit()
    return jsonify({"msg": f"Company active status changed to {company.is_active}"}), 200

@admin_bp.route('/students', methods=['GET'])
@role_required('admin')
def get_students():
    students = StudentProfile.query.all()
    result = []
    for s in students:
        result.append({
            "id": s.id,
            "name": s.name,
            "branch": s.branch,
            "cgpa": s.cgpa,
            "year": s.year,
            "is_active": s.is_active
        })
    return jsonify(result), 200

@admin_bp.route('/students/<int:student_id>/blacklist', methods=['PUT'])
@role_required('admin')
def blacklist_student(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    student.is_active = not student.is_active
    db.session.commit()
    status = "activated" if student.is_active else "blacklisted"
    return jsonify({"msg": f"Student {status} successfully"}), 200

@admin_bp.route('/trigger-notifications', methods=['POST'])
@role_required('admin')
def trigger_notifications():
    from models import Notification
    from datetime import datetime, timedelta
    
    tomorrow = datetime.utcnow() + timedelta(days=1)
    drives = PlacementDrive.query.filter_by(status='Approved').all()
    closing_drives = [d for d in drives if d.application_deadline and d.application_deadline.date() == tomorrow.date()]
    
    students = StudentProfile.query.filter_by(is_active=True).all()
    
    count = 0
    if closing_drives:
        for drive in closing_drives:
            msg = f"Reminder: Drive '{drive.job_title}' by {drive.company_profile.company_name} is closing tomorrow!"
            for student in students:
                db.session.add(Notification(user_id=student.user_id, message=msg))
                count += 1
    
    # Generic welcome message if no drives are closing (for testing purposes)
    if count == 0:
        for student in students:
            db.session.add(Notification(user_id=student.user_id, message="Reminder: Keep your profile updated for upcoming placement drives!"))
            count += 1
            
    db.session.commit()
    return jsonify({"msg": f"Successfully sent {count} notifications to active students."}), 200

@admin_bp.route('/drives', methods=['GET'])
@role_required('admin')
def get_drives():
    drives = PlacementDrive.query.all()
    result = []
    for d in drives:
        result.append({
            "id": d.id,
            "company_name": d.company_profile.company_name,
            "job_title": d.job_title,
            "status": d.status,
            "application_deadline": d.application_deadline.strftime('%Y-%m-%d') if d.application_deadline else "",
            "applicant_count": len(d.applications)
        })
    return jsonify(result), 200

@admin_bp.route('/broadcast-email', methods=['POST'])
@role_required('admin')
def admin_broadcast_email():
    data = request.get_json()
    subject = data.get('subject')
    body = data.get('body')
    
    if not subject or not body:
        return jsonify({"msg": "Subject and body are required"}), 400
        
    from tasks import broadcast_email_task
    broadcast_email_task.delay(subject, body)
    
    return jsonify({"msg": "Broadcast email queued successfully. Sending in the background."}), 200

@admin_bp.route('/report/pdf', methods=['GET'])
@role_required('admin')
def generate_pdf_report():
    total_drives = PlacementDrive.query.count()
    total_apps = Application.query.count()
    selected_apps = Application.query.filter_by(status='Selected').count()
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, f"Placement Portal Monthly Report - {datetime.now().strftime('%B %Y')}")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 710, f"Total Drives Conducted/Created: {total_drives}")
    p.drawString(100, 690, f"Total Student Applications: {total_apps}")
    p.drawString(100, 670, f"Total Students Selected: {selected_apps}")
    
    p.drawString(100, 630, "Drive Breakdown:")
    y_pos = 610
    
    drives = PlacementDrive.query.all()
    for d in drives:
        selected_in_drive = Application.query.filter_by(drive_id=d.id, status='Selected').count()
        p.drawString(120, y_pos, f"- {d.job_title} ({d.company_profile.company_name}): {len(d.applications)} applicants, {selected_in_drive} selected")
        y_pos -= 20
        if y_pos < 100:
            p.showPage()
            y_pos = 750
            
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"placement_report_{datetime.now().strftime('%Y_%m')}.pdf",
        mimetype="application/pdf"
    )

@admin_bp.route('/drives/<int:drive_id>/status', methods=['PUT'])
@role_required('admin')
def update_drive_status(drive_id):
    data = request.get_json()
    new_status = data.get('status')
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = new_status
    db.session.commit()
    return jsonify({"msg": f"Drive status updated to {new_status}"}), 200
