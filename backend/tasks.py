from celery_worker import celery
from models import db, PlacementDrive, Application, User, StudentProfile, CompanyProfile, Notification
from datetime import datetime, timedelta
import csv
import os

@celery.task
def send_email_notification(to_email, subject, body):
    import smtplib
    from email.mime.text import MIMEText
    
    sender_email = os.environ.get('MAIL_USERNAME', 'dummy@example.com')
    password = os.environ.get('MAIL_PASSWORD', 'dummy_password')
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    
    if password != 'dummy_password':
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, to_email, msg.as_string())
            print(f"[EMAIL] Sent email to {to_email}: {subject}")
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send email to {to_email}: {str(e)}")
    else:
        print(f"[EMAIL SIMULATED] To: {to_email} | Subject: {subject} | Body: {body}")
        
    return f"Email processed for {to_email}"

@celery.task
def send_daily_reminders():
    tomorrow = datetime.utcnow() + timedelta(days=1)
    
    # We load manually since db.func.date isn't straightforward across SQLite/Postgres sometimes
    drives = PlacementDrive.query.filter_by(status='Approved').all()
    closing_drives = [d for d in drives if d.application_deadline and d.application_deadline.date() == tomorrow.date()]
    
    if closing_drives:
        students = StudentProfile.query.filter_by(is_active=True).all()
        for drive in closing_drives:
            msg = f"Reminder: Drive '{drive.job_title}' by {drive.company_profile.company_name} is closing tomorrow!"
            print(f"[REMINDER] {msg}")
            
            email_count = 0
            for student in students:
                db.session.add(Notification(user_id=student.user_id, message=msg))
                # Send Email
                student_user = User.query.get(student.user_id)
                if student_user and student_user.email:
                    send_email_notification.apply_async(
                        args=[student_user.email, "Placement Drive Deadline Reminder", msg],
                        countdown=email_count * 5  # 5 seconds breathing space between emails
                    )
                    email_count += 1
                    
        db.session.commit()
        
    return f"Sent reminders for {len(closing_drives)} drives"

@celery.task
def broadcast_email_task(subject, body):
    students = StudentProfile.query.filter_by(is_active=True).all()
    count = 0
    for student in students:
        student_user = User.query.get(student.user_id)
        if student_user and student_user.email:
            send_email_notification.apply_async(
                args=[student_user.email, subject, body],
                countdown=count * 5  # 5 seconds breathing space between emails
            )
            count += 1
    
    print(f"[BROADCAST] Queued emails for {count} active students.")
    return f"Broadcasted to {count} students"

@celery.task
def generate_monthly_report():
    total_drives = PlacementDrive.query.count()
    total_apps = Application.query.count()
    selected_apps = Application.query.filter_by(status='Selected').count()
    
    html_content = f"""
    <html>
        <body>
            <h1>Monthly Placement Report ({datetime.now().strftime("%B %Y")})</h1>
            <p>Total Drives Conducted: {total_drives}</p>
            <p>Total Applications Received: {total_apps}</p>
            <p>Total Students Selected: {selected_apps}</p>
        </body>
    </html>
    """
    print(f"[REPORT] HTML Report generated. Simulating sending email to admin...\n{html_content}")
    return "Monthly report generated"

@celery.task
def export_applications_csv(student_id):
    apps = Application.query.filter_by(student_id=student_id).all()
    
    # Save the file in a static or downloads directory
    export_dir = os.path.join(os.path.dirname(__file__), 'exports')
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
        
    filename = f"export_{student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    filepath = os.path.join(export_dir, filename)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Application ID', 'Company Name', 'Drive Title', 'Application Status', 'Date'])
        for app in apps:
            writer.writerow([
                app.id,
                app.placement_drive.company_profile.company_name,
                app.placement_drive.job_title,
                app.status,
                app.application_date.strftime('%Y-%m-%d')
            ])
            
    # Send Notification to Student
    student = StudentProfile.query.get(student_id)
    if student:
        msg = f"Your applications history export is ready. Download it here: /api/student/download/{filename}"
        db.session.add(Notification(user_id=student.user_id, message=msg))
        db.session.commit()
            
    print(f"[EXPORT] Created CSV for student {student_id} at {filepath}")
    return filename
