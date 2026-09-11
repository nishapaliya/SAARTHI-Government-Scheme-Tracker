from services.email_service import send_email
import random
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database.db import query_db, execute_db


applications_bp = Blueprint('applications', __name__, url_prefix='/applications')

@applications_bp.route('/wizard/<int:scheme_id>')
def application_wizard(scheme_id):
    if 'user_id' not in session:
        flash("Please log in to apply for government schemes.", "warning")
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    scheme = query_db("SELECT * FROM schemes WHERE id = ?", (scheme_id,), one=True)
    
    if not scheme:
        flash("Invalid Scheme requested.", "danger")
        return redirect(url_for('schemes.list_schemes'))
        
    # Check if already applied
    existing = query_db("SELECT * FROM applications WHERE user_id = ? AND scheme_id = ?", (user_id, scheme_id), one=True)
    if existing:
        flash(f"You have already submitted an application for {scheme['title']} (Ref: {existing['application_ref']}).", "info")
        return redirect(url_for('applications.application_tracker', ref=existing['application_ref']))

    # Parse the scheme's required documents into a clean list for Step 3
    raw_docs = scheme.get('documents_required') or "Aadhaar Card, Income Certificate, Bank Passbook Copy"
    required_docs = [d.strip() for d in raw_docs.split(',') if d.strip()]

    # Pull the citizen's already-verified Digital Vault documents so they can be
    # attached directly instead of re-uploading/re-verifying.
    vault_docs = query_db(
        "SELECT * FROM documents WHERE user_id = ? AND verification_status = 'verified' ORDER BY uploaded_at DESC",
        (user_id,)
    )

    return render_template(
        'applications/wizard.html',
        user=user,
        scheme=scheme,
        required_docs=required_docs,
        vault_docs=vault_docs
    )

@applications_bp.route('/submit', methods=['POST'])
def submit_application():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized. Please login.'}), 401
        
    user_id = session['user_id']
    scheme_id = request.form.get('scheme_id')
    user = query_db(
    "SELECT full_name, email FROM users WHERE id = ?",
    (user_id,),
    one=True
)
    
    scheme = query_db("SELECT * FROM schemes WHERE id = ?", (scheme_id,), one=True)
    if not scheme:
        return jsonify({'success': False, 'message': 'Scheme not found.'}), 404
        
    # Generate unique ref number
    ref_num = f"SRT-{datetime.datetime.now().year}-{random.randint(10000, 99999)}"
    
    # Save Application to Database
    app_id = execute_db('''
    INSERT INTO applications (application_ref, user_id, scheme_id, status, applied_date, remarks)
    VALUES (?, ?, ?, 'submitted', CURRENT_TIMESTAMP, 'Application submitted via Saarthi Single Window Portal.')
    ''', (ref_num, user_id, scheme_id))
    
    # Create notification for user
    execute_db('''
    INSERT INTO notifications (user_id, title, message, type)
    VALUES (?, 'Application Submitted', ?, 'info')
    ''', (user_id, f"Your application for {scheme['title']} has been received. Reference ID: {ref_num}"))
    
    # Auto-add a reminder for field scrutiny
    due_date = (datetime.date.today() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    execute_db('''
    INSERT INTO reminders (user_id, title, due_date, reminder_type, description)
    VALUES (?, ?, ?, 'scrutiny', ?)
    ''', (user_id, f"Scrutiny Target: {ref_num}", due_date, f"Expected initial officer review for {scheme['title']}."))

    # Attach the documents chosen/uploaded in Step 3 (Document Vault step) of the
    # wizard to this application. These are documents already sitting in the
    # citizen's Digital Vault (verification_status='verified') — either just
    # uploaded+OCR-verified during this session, or picked from previously
    # verified vault documents. No re-verification happens here.
    document_ids = request.form.getlist('document_ids[]') or request.form.getlist('document_ids')
    for doc_id in document_ids:
        if not doc_id:
            continue
        execute_db(
            "UPDATE documents SET application_id = ? WHERE id = ? AND user_id = ? AND verification_status = 'verified'",
            (app_id, doc_id, user_id)
        )

    # Send Application Submission Email
    html = f"""
        <h2>Application Submitted Successfully</h2>
    
        <p>Dear {user['full_name']},</p>
    
        <p>Your application has been submitted successfully.</p>
    
        <p><b>Application Reference:</b> {ref_num}</p>
        <p><b>Scheme:</b> {scheme['title']}</p>
        <p><b>Status:</b> Submitted</p>
    
        <p>You can track your application anytime through the Saarthi portal.</p>
    
        <hr>
    
        <p>Thank you,<br>Saarthi Team</p>
        """
    
    try:
        send_email(
                user["email"],
                user["full_name"],
                "Application Submitted Successfully",
                html
            )
    except Exception as e:
        print(f"Brevo Email Error: {e}")

    
    return jsonify({
        'success': True,
        'application_ref': ref_num,
        'redirect_url': url_for('applications.application_tracker', ref=ref_num)
    })
    

@applications_bp.route('/tracker/<ref>')
def application_tracker(ref):
    if 'user_id' not in session:
        flash("Please log in to track applications.", "warning")
        return redirect(url_for('auth.login'))
        
    app_data = query_db('''
    SELECT a.*, s.title as scheme_title, s.category as scheme_category, s.benefit_amount, s.ministry,
           u.full_name as applicant_name, u.aadhaar_no, u.dbt_bank_account, u.bank_name, u.ifsc_code
    FROM applications a
    JOIN schemes s ON a.scheme_id = s.id
    JOIN users u ON a.user_id = u.id
    WHERE a.application_ref = ?
    ''', (ref,), one=True)
    
    if not app_data:
        flash("Application Reference Number not found.", "danger")
        return redirect(url_for('citizen_dashboard'))
        
    # Check permissions
    if session.get('role') != 'admin' and app_data['user_id'] != session.get('user_id'):
        flash("Unauthorized access to this application record.", "danger")
        return redirect(url_for('citizen_dashboard'))
        
    docs = query_db("SELECT * FROM documents WHERE application_id = ?", (app_data['id'],))
    
    return render_template('applications/tracker.html', app=app_data, docs=docs)

@applications_bp.route('/api/status-update', methods=['POST'])
def update_status():
    """Allows Admin/Nodal Officers to approve, reject, or advance application statuses and trigger simulated DBT."""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Permission denied. Admin access required.'}), 403
        
    data = request.get_json() or {}
    app_id = data.get('app_id')
    new_status = data.get('status')
    remarks = data.get('remarks', '')
    rejection_reason = data.get('rejection_reason', '')
    
    app_record = query_db('''
    SELECT a.*, s.benefit_amount, s.title as scheme_title,
       u.id as user_id,
       u.full_name,
       u.email
        FROM applications a
        JOIN schemes s ON a.scheme_id = s.id
        JOIN users u ON a.user_id = u.id
        WHERE a.id = ?
    ''', (app_id,), one=True)
    
    if not app_record:
        return jsonify({'success': False, 'message': 'Application not found.'}), 404
        
    
    
    if new_status == 'disbursement_in_progress':
        
        # Trigger success notification
        execute_db('''
    INSERT INTO notifications (user_id, title, message, type)
    VALUES (?, 'Disbursement In Progress', ?, 'info')
    ''', (
            app_record['user_id'],
        f"Your application for {app_record['scheme_title']} has been forwarded to the Government Department for benefit disbursement."
        ))

        html = f"""
        <h2>🏛️ Application Forwarded</h2>

        <p>Dear <b>{app_record['full_name']}</b>,</p>

        <p>We are pleased to inform you that your application has been approved.</p>

        <p><b>Current Status:</b> <span style="color:#0d6efd;"><b>Disbursement In Progress</b></span></p>

        <p>Your application has been forwarded to the Government Department for processing of the benefit.</p>

        <p><b>Application Reference:</b> {app_record['application_ref']}</p>

        <p><b>Scheme:</b> {app_record['scheme_title']}</p>

        <p>You will receive another notification once the Government completes the disbursement process.</p>

        <hr>

        <p>Regards,<br>
        SAARTHI Government Portal</p>
        """

        try:
            send_email(
                app_record["email"],
                app_record["full_name"],
                "🏛️ Disbursement In Progress",
                html
            )
        except Exception as e:
            print(f"Email Error: {e}")

    elif new_status == 'approved':
        execute_db('''
        INSERT INTO notifications (user_id, title, message, type)
        VALUES (?, 'Application Approved', ?, 'success')
        ''', (app_record['user_id'], f"Your application {app_record['application_ref']} for {app_record['scheme_title']} has been approved by the Nodal Officer."))
        html = f"""
            <h2>🎉 Application Approved</h2>

            <p>Dear <b>{app_record['full_name']}</b>,</p>

            <p>Congratulations! Your application has been <b style="color:green;">APPROVED</b>.</p>

            <p><b>Application Reference:</b> {app_record['application_ref']}</p>

            <p><b>Scheme:</b> {app_record['scheme_title']}</p>

            <p>You can now log in to SAARTHI to view your application status.</p>

            <hr>

            <p>Regards,<br>
            SAARTHI Government Portal</p>
            """

        try:
            send_email(
                    app_record["email"],
                    app_record["full_name"],
                    "🎉 Application Approved",
                    html
                )
        except Exception as e:
            print(f"Email Error: {e}")

    elif new_status == 'rejected':
        execute_db('''
        INSERT INTO notifications (user_id, title, message, type)
        VALUES (?, 'Application Update: Action Required', ?, 'danger')
        ''', (app_record['user_id'],
               f"Your application {app_record['application_ref']} was not approved. Reason: {rejection_reason}"))
        html = f"""
<h2>❌ Application Rejected</h2>

<p>Dear <b>{app_record['full_name']}</b>,</p>

<p>We regret to inform you that your application has been <b style="color:red;">REJECTED</b>.</p>

<p><b>Application Reference:</b> {app_record['application_ref']}</p>

<p><b>Scheme:</b> {app_record['scheme_title']}</p>

<p><b>Reason:</b> {rejection_reason}</p>

<p>Please review the reason above, correct the issue (if applicable), and submit a fresh application if you remain eligible.</p>

<hr>

<p>Regards,<br>
SAARTHI Government Portal</p>
"""

        try:
            send_email(
                app_record["email"],
                app_record["full_name"],
                "❌ Application Rejected",
                html
            )
        except Exception as e:
            print(f"Email Error: {e}")
    execute_db('''
UPDATE applications
SET
status = ?,
remarks = ?,
rejection_reason = ?,
updated_at = CURRENT_TIMESTAMP
WHERE id = ?
''',
(
'disbursement_in_progress' if new_status == 'disbursement_in_progress' else new_status,
remarks,
rejection_reason,
app_id
))    
    return jsonify({

    "success":True,

    "message":f"Application {app_record['application_ref']} updated successfully."

})