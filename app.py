import datetime
import random
import os
from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
from config import Config
from database.db import init_db, query_db, execute_db

# Grievance attachment upload settings
GRIEVANCE_UPLOAD_FOLDER = os.path.join('static', 'uploads', 'grievances')
GRIEVANCE_ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}
GRIEVANCE_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def _is_allowed_grievance_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in GRIEVANCE_ALLOWED_EXTENSIONS

# Import Blueprints
from modules.auth.routes import auth_bp
from modules.schemes.routes import schemes_bp
from modules.applications.routes import applications_bp
from modules.documents.routes import documents_bp
from modules.notifications.routes import notifications_bp
from modules.analytics.routes import analytics_bp
from modules.chatbot.routes import chatbot_bp
from modules.export.routes import export_bp
from modules.reminders.routes import reminders_bp
from modules.helpdesk.routes import helpdesk_bp


load_dotenv()
app = Flask(__name__)


print("=" * 60)
print("RUNNING PROJECT FROM:", os.path.abspath(os.path.dirname(__file__)))
print("=" * 60)
app.config.from_object(Config)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(schemes_bp)
app.register_blueprint(applications_bp)
app.register_blueprint(documents_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(export_bp)
app.register_blueprint(reminders_bp)
app.register_blueprint(helpdesk_bp)

# Context processor for topbar notifications & current user
@app.context_processor
def inject_global_vars():
    user = None
    unread_count = 0
    if 'user_id' in session:
        user = query_db("SELECT * FROM users WHERE id = ?", (session['user_id'],), one=True)
        res = query_db("SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = 0", (session['user_id'],), one=True)
        unread_count = res['count'] if res else 0
    return dict(current_user=user, unread_count=unread_count)

# Primary Routes
@app.route("/")
def index():
    featured_schemes = query_db(
        "SELECT * FROM schemes WHERE status='active' ORDER BY id ASC LIMIT 6"
    )

    scheme_count = query_db("SELECT COUNT(*) as count FROM schemes WHERE status='active'", one=True)
    citizen_count = query_db("SELECT COUNT(*) as count FROM users WHERE role='citizen'", one=True)
    application_count = query_db("SELECT COUNT(*) as count FROM applications", one=True)
    disbursed_row = query_db("SELECT SUM(disbursed_amount) as total FROM applications WHERE status='disbursed'", one=True)

    stats = {
        "total_schemes": (scheme_count['count'] if scheme_count else 0),
        "total_citizens": (citizen_count['count'] if citizen_count else 0),
        "total_applications": (application_count['count'] if application_count else 0),
        "total_disbursed": (disbursed_row['total'] if disbursed_row and disbursed_row['total'] else 0)
    }

    return render_template(
        "index.html",
        featured_schemes=featured_schemes,
        stats=stats
    )
    
@app.route('/citizen/dashboard')
def citizen_dashboard():
    if 'user_id' not in session:
        flash("Please log in to access the Citizen Dashboard.", "warning")
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    
    applications = query_db('''
    SELECT a.*, s.title as scheme_title, s.category, s.benefit_amount, s.ministry
    FROM applications a
    JOIN schemes s ON a.scheme_id = s.id
    WHERE a.user_id = ?
    ORDER BY a.id DESC
    ''', (user_id,))
    
    total_disbursed = sum(a['disbursed_amount'] or 0.0 for a in applications)
    documents = query_db("SELECT * FROM documents WHERE user_id = ? ORDER BY uploaded_at DESC LIMIT 5", (user_id,))
    reminders = query_db("SELECT * FROM reminders WHERE user_id = ? AND is_completed = 0 ORDER BY due_date ASC LIMIT 5", (user_id,))
    notifications = query_db("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", (user_id,))
    
    # Recommended schemes
    recommended = query_db("SELECT * FROM schemes WHERE status = 'active' ORDER BY benefit_amount DESC LIMIT 4")

    return render_template('citizen/dashboard.html', 
                           user=user, 
                           applications=applications, 
                           total_disbursed=total_disbursed,
                           documents=documents, 
                           reminders=reminders, 
                           notifications=notifications,
                           recommended=recommended)

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Admin credentials required to view Nodal Officer Portal.", "danger")
        return redirect(url_for('auth.login'))
        
    status_filter = request.args.get('status', 'All')
    search_q = request.args.get('q', '').strip()
    
    query = '''
    SELECT a.*, s.title as scheme_title, s.category as scheme_category, s.benefit_amount,
           u.full_name as applicant_name, u.aadhaar_no, u.state, u.district
    FROM applications a
    JOIN schemes s ON a.scheme_id = s.id
    JOIN users u ON a.user_id = u.id
    WHERE 1=1
    '''
    params = []
    
    if status_filter != 'All':
        query += " AND a.status = ?"
        params.append(status_filter)
        
    if search_q:
        query += " AND (a.application_ref LIKE ? OR u.full_name LIKE ? OR s.title LIKE ? OR u.aadhaar_no LIKE ?)"
        params.extend([f"%{search_q}%", f"%{search_q}%", f"%{search_q}%", f"%{search_q}%"])
        
    query += " ORDER BY a.id DESC"
    applications = query_db(query, tuple(params))
    
    schemes = query_db("SELECT * FROM schemes ORDER BY id ASC")
    
    return render_template('admin/dashboard.html', applications=applications, schemes=schemes, selected_status=status_filter, search_q=search_q)

@app.route('/grievances', methods=['GET', 'POST'])
def grievances():
    if 'user_id' not in session:
        flash("Please log in to lodge or view support grievances.", "warning")
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()
        app_id = request.form.get('application_id', None)

        # --- Optional attachment handling ---
        attachment_path = None
        upload_file = request.files.get('attachment')

        if upload_file and upload_file.filename != '':
            filename = secure_filename(upload_file.filename)

            if not _is_allowed_grievance_file(filename):
                flash("Attachment must be a JPG, JPEG, PNG, or PDF file.", "danger")
                return redirect(url_for('grievances'))

            # Enforce 5 MB max size (checked after reading, since browsers
            # don't reliably report Content-Length per-file in multipart forms)
            upload_file.seek(0, os.SEEK_END)
            file_size = upload_file.tell()
            upload_file.seek(0)

            if file_size > GRIEVANCE_MAX_FILE_SIZE:
                flash("Attachment exceeds the 5 MB size limit.", "danger")
                return redirect(url_for('grievances'))

            os.makedirs(GRIEVANCE_UPLOAD_FOLDER, exist_ok=True)

            # Prefix with user id + timestamp to avoid filename collisions between citizens
            unique_name = f"{user_id}_{int(datetime.datetime.now().timestamp())}_{filename}"
            save_path = os.path.join(GRIEVANCE_UPLOAD_FOLDER, unique_name)
            upload_file.save(save_path)

            # Stored as a relative static path so it can be rendered directly with url_for('static', filename=...)
            attachment_path = f"uploads/grievances/{unique_name}"

        ticket_no = f"GRV-{datetime.datetime.now().year}-{random.randint(1000, 9999)}"
        execute_db('''
        INSERT INTO grievances (ticket_no, user_id, application_id, subject, description, status, attachment)
        VALUES (?, ?, ?, ?, ?, 'open', ?)
        ''', (ticket_no, user_id, app_id, subject, description, attachment_path))
        
        flash(f"Grievance Ticket {ticket_no} submitted successfully. Nodal Helpdesk will respond shortly.", "success")
        return redirect(url_for('grievances'))
        
    user_grievances = query_db("SELECT * FROM grievances WHERE user_id = ? ORDER BY id DESC", (user_id,))
    apps = query_db("SELECT id, application_ref FROM applications WHERE user_id = ?", (user_id,))
    
    return render_template('citizen/grievances.html', grievances=user_grievances, applications=apps)

if __name__ == '__main__':
    # Initialize DB schema & seed data
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 SAARTHI National Portal Server starting on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)