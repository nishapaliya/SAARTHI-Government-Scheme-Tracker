import io
import csv
from flask import Blueprint, render_template, make_response, session, flash, redirect, url_for, send_file
from database.db import query_db

export_bp = Blueprint('export', __name__, url_prefix='/export')

@export_bp.route('/application-slip/<ref>')
def download_application_slip(ref):
    if 'user_id' not in session:
        flash("Login required to download application receipts.", "warning")
        return redirect(url_for('auth.login'))
        
    app_data = query_db('''
    SELECT a.*, s.title as scheme_title, s.category as scheme_category, s.benefit_amount, s.ministry,
           u.full_name as applicant_name, u.aadhaar_no, u.dbt_bank_account, u.bank_name, u.ifsc_code, u.state, u.district
    FROM applications a
    JOIN schemes s ON a.scheme_id = s.id
    JOIN users u ON a.user_id = u.id
    WHERE a.application_ref = %s
    ''', (ref,), one=True)
    
    if not app_data:
        return "Application Slip Not Found", 404
        
    return render_template('applications/receipt.html', app=app_data)

@export_bp.route('/dbt-ledger-csv')
def export_dbt_ledger_csv():
    if 'user_id' not in session:
        return "Unauthorized", 401
        
    user_id = session['user_id']
    role = session.get('role')
    
    if role == 'admin':
        records = query_db('''
        SELECT a.application_ref, u.full_name, u.aadhaar_no, s.title as scheme_name, a.status, 
               a.disbursed_amount, a.dbt_transaction_id, a.applied_date
        FROM applications a
        JOIN users u ON a.user_id = u.id
        JOIN schemes s ON a.scheme_id = s.id
        ORDER BY a.id DESC
        ''')
    else:
        records = query_db('''
        SELECT a.application_ref, u.full_name, u.aadhaar_no, s.title as scheme_name, a.status, 
               a.disbursed_amount, a.dbt_transaction_id, a.applied_date
        FROM applications a
        JOIN users u ON a.user_id = u.id
        JOIN schemes s ON a.scheme_id = s.id
        WHERE a.user_id = %s
        ORDER BY a.id DESC
        ''', (user_id,))
        
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Application Ref', 'Beneficiary Name', 'Aadhaar Masked', 'Scheme Name', 'Status', 'Disbursed Amount (INR)', 'DBT Tx ID', 'Applied Date'])
    
    for r in records:
        masked_aadhaar = f"XXXX-XXXX-{r['aadhaar_no'][-4:]}" if r['aadhaar_no'] else 'N/A'
        writer.writerow([
            r['application_ref'],
            r['full_name'],
            masked_aadhaar,
            r['scheme_name'],
            r['status'].upper(),
            f"{r['disbursed_amount']:.2f}",
            r['dbt_transaction_id'] or 'N/A',
            r['applied_date'].strftime("%d-%m-%Y") if r['applied_date'] else ""
        ])
        
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=saarthi_dbt_ledger_export.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@export_bp.route('/generate-static-chart')
def generate_static_chart():
    """Generates a static PNG chart using Matplotlib for printable reports."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        data = query_db('''
        SELECT s.category, SUM(a.disbursed_amount) as amount
        FROM schemes s
        LEFT JOIN applications a ON s.id = a.scheme_id
        GROUP BY s.category
        ''')
        
        categories = [d['category'] for d in data]
        amounts = [float(d['amount'] or 0.0) for d in data]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(categories, amounts, color='#1565C0')
        ax.set_title('Sector-Wise DBT Allocation (INR)', fontsize=12, fontweight='bold', color='#0D47A1')
        ax.set_ylabel('Amount in ₹', fontsize=10)
        plt.xticks(rotation=30, ha='right', fontsize=9)
        plt.tight_layout()

        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png', dpi=150)
        img_buf.seek(0)
        plt.close(fig)

        return send_file(img_buf, mimetype='image/png')
    except Exception as e:
        return f"Matplotlib chart generation notice: {e}", 500
