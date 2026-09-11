from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import query_db, execute_db
from services.email_service import send_email

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = query_db(
            "SELECT * FROM users WHERE email = ?",
            (email,),
            one=True
        )

        if not user:
            user = query_db(
                "SELECT * FROM users WHERE aadhaar_no = ?",
                (email,),
                one=True
            )

        if not password:
            flash("Password is required.", "danger")
            return render_template("auth/login.html")

        print("=" * 50)
        print("User Found:", user is not None)

        if user:
            print("Email:", user["email"])
            print("Stored Hash:", user["password_hash"])
            print("Password Entered:", password)
            print("Password Match:", check_password_hash(user["password_hash"], password))

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            session["aadhaar_no"] = user["aadhaar_no"]

            flash(f"Welcome back, {user['full_name']}!", "success")

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("citizen_dashboard"))

        flash("Invalid credentials or Aadhaar number. Please check your login details.", "danger")

    return render_template("auth/login.html")
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        aadhaar_no = request.form.get('aadhaar_no', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '')
        dob = request.form.get('dob', '')
        gender = request.form.get('gender', 'Male')
        category = request.form.get('category', 'General')
        income = float(request.form.get('income_annual', 0))
        occupation = request.form.get('occupation', 'Citizen')
        state = request.form.get('state', 'Delhi')
        district = request.form.get('district', 'New Delhi')
        bank_acc = request.form.get('dbt_bank_account', '')
        ifsc = request.form.get('ifsc_code', '').strip().upper()
       # IFSC Validation
        if len(ifsc) != 11:
            flash("IFSC Code must be exactly 11 characters.", "warning")
            return render_template('auth/register.html')
       
        bank_name = request.form.get('bank_name', 'State Bank of India')
                # Bank Account Validation
        if not bank_acc.isdigit():
            flash("Bank Account Number must contain only digits.", "warning")
            return render_template('auth/register.html')

        if len(bank_acc) < 9 or len(bank_acc) > 18:
            flash("Bank Account Number must be between 9 and 18 digits.", "warning")
            return render_template('auth/register.html')
                

        
        # Validation
        if len(aadhaar_no) != 12 or not aadhaar_no.isdigit():
            flash("Aadhaar Number must be exactly 12 numeric digits.", "warning")
            return render_template('auth/register.html')
            
        existing = query_db("SELECT id FROM users WHERE email = ? OR aadhaar_no = ?", (email, aadhaar_no), one=True)
        if existing:
            flash("An account with this Email or Aadhaar Number already exists.", "danger")
            return render_template('auth/register.html')
            
        pwd_hash = generate_password_hash(password)
        
        user_id = execute_db('''
        INSERT INTO users (aadhaar_no, full_name, email, mobile, password_hash, role, dob, gender, category, income_annual, occupation, state, district, dbt_bank_account, ifsc_code, bank_name, dbt_linked, profile_completed)
        VALUES (?, ?, ?, ?, ?, 'citizen', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 90)
        ''', (aadhaar_no, full_name, email, mobile, pwd_hash, dob, gender, category, income, occupation, state, district, bank_acc, ifsc, bank_name))
        
        # Add welcome notification
        execute_db('''
        INSERT INTO notifications (user_id, title, message, type)
        VALUES (?, 'e-KYC Account Created', 'Your Saarthi Citizen Benefit profile has been created & verified via Aadhaar e-KYC.', 'success')
        ''', (user_id,))
        
        # Send Welcome Email
        html = f"""
        <h2>Welcome to Saarthi, {full_name}!</h2>

        <p>Your account has been created successfully.</p>

        <p><b>Aadhaar:</b> {aadhaar_no}</p>
        <p><b>Email:</b> {email}</p>

        <p>You can now login and apply for Government Schemes.</p>

        <hr>

        <p>Thank you for choosing Saarthi.</p>
        """

        try:
            send_email(
                email,
                full_name,
                "Welcome to Saarthi",
                html
            )
        except Exception as e:
            print("Email Error:", e)


        flash("Registration & Aadhaar e-KYC Verification successful! Please login to continue.", "success")
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('index'))

@auth_bp.route('/api/ekyc-verify', methods=['POST'])
def api_ekyc_verify():
    """Simulates instant government Aadhaar e-KYC OTP verification."""
    data = request.get_json() or {}
    aadhaar = data.get('aadhaar_no', '')
    
    if len(aadhaar) == 12 and aadhaar.isdigit():
        return jsonify({
            'success': True,
            'message': 'Aadhaar e-KYC Verified Successfully via UIDAI Gateway',
            'details': {
                'full_name': 'Verified Citizen (UIDAI Record)',
                'gender': 'Male',
                'dob': '1992-06-15',
                'state': 'Uttar Pradesh',
                'address_verified': True
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid 12-digit Aadhaar Number.'}), 400