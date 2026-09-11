from ai.document_ai import verify_document, is_document_verified
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from config import Config
from database.db import query_db, execute_db

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')


@documents_bp.route('/vault')
def vault():
    if 'user_id' not in session:
        flash("Please login to access your Digital Document Vault.", "warning")
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    docs = query_db("SELECT * FROM documents WHERE user_id = ? ORDER BY uploaded_at DESC", (user_id,))
    return render_template('citizen/document_vault.html', docs=docs)


@documents_bp.route('/upload', methods=['POST'])
def upload_document():
    print("STEP 1 - Upload route entered")
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    user_id = session['user_id']
    doc_type = request.form.get('doc_type', 'Verification Document')
    app_id = request.form.get('application_id', None)

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file file part in request.'}), 400

    file = request.files['file']
    print("STEP 2 - File received:", file.filename)

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected.'}), 400

    filename = secure_filename(file.filename)
    print("STEP 3 - Filename:", filename)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(save_path)
    print("STEP 4 - File saved:", save_path)

    ext = os.path.splitext(filename)[1].lower()
    print("STEP 5 - Extension:", ext)

    if ext not in [".jpg", ".jpeg", ".png", ".pdf"]:
        return jsonify({
            "success": False,
            "message": "Only JPG, JPEG and PNG images are supported for AI verification."
        }), 400
    print("STEP 6 - Extension Accepted")

        # Check duplicate BEFORE OCR
    existing = query_db(
        """
        SELECT id
        FROM documents
        WHERE user_id = ?
        AND doc_type = ?
        AND file_name = ?
        """,
        (user_id, doc_type, filename)
    )

    if existing:

        if os.path.exists(save_path):
            os.remove(save_path)

        return jsonify({
            "success": False,
            "message": "This document has already been uploaded to your vault.",
            "verification": "Duplicate document detected."
        }), 400

    # Run OCR only if not duplicate
    try:
        ai_report = verify_document(save_path, doc_type)

    except Exception as e:
        print("AI Verification Error:", e)
        ai_report = f"Verification Failed: {e}"

    print(ai_report)
    print("AI REPORT =", ai_report)

    if not is_document_verified(ai_report):

        if os.path.exists(save_path):
            os.remove(save_path)

        return jsonify({
            "success": False,
            "message": "Document verification failed.",
            "verification": ai_report
        }), 400
    doc_id = execute_db('''

INSERT INTO documents(

user_id,
application_id,
doc_type,
file_name,
file_path,
file_size,
verification_status,
ai_report

)

VALUES(

?,
?,
?,
?,
?,
?,
?,
?

)

''',

    (

        user_id,
        app_id,
        doc_type,
        filename,
        f"uploads/{filename}",
        os.path.getsize(save_path),
        "verified",
        ai_report

    ))

    return jsonify({
        'success': True,
        'message': f"{doc_type} uploaded successfully ",
        "verification": ai_report,
        'doc_id': doc_id,
        'file_name': filename
    })


@documents_bp.route('/delete/<int:doc_id>', methods=['POST'])
def delete_document(doc_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    execute_db("DELETE FROM documents WHERE id = ? AND user_id = ?", (doc_id, session['user_id']))
    return jsonify({'success': True, 'message': 'Document deleted.'})


@documents_bp.route('/application/<int:app_id>')
def view_application_documents(app_id):
    """
    Admin 'View Documents' page: lists every document already uploaded
    (via the existing Digital Vault / /documents/upload flow) for a given
    application. Reuses the 'documents' table - no new upload/storage path.
    """
    if 'user_id' not in session:
        flash("Please log in to view application documents.", "warning")
        return redirect(url_for('auth.login'))

    app_data = query_db('''
        SELECT a.*, s.title as scheme_title, u.full_name as applicant_name
        FROM applications a
        JOIN schemes s ON a.scheme_id = s.id
        JOIN users u ON a.user_id = u.id
        WHERE a.id = ?
    ''', (app_id,), one=True)

    if not app_data:
        flash("Application not found.", "danger")
        return redirect(url_for('citizen_dashboard'))

    # Admins can view any application's documents; citizens only their own.
    if session.get('role') != 'admin' and app_data['user_id'] != session.get('user_id'):
        flash("Unauthorized access to this application's documents.", "danger")
        return redirect(url_for('citizen_dashboard'))

    docs = query_db(
        "SELECT * FROM documents WHERE application_id = ? ORDER BY uploaded_at DESC",
        (app_id,)
    )

    return render_template('documents/application_documents.html', app=app_data, docs=docs)


@documents_bp.route('/file/<int:doc_id>')
def serve_file(doc_id):
    """
    Streams a previously uploaded document from Config.UPLOAD_FOLDER.
    Same physical file the Vault/upload flow already saved - nothing is duplicated.
    Images/PDFs open inline (browser's native viewer); ?download=1 forces a download.
    """
    if 'user_id' not in session:
        flash("Please log in to view this document.", "warning")
        return redirect(url_for('auth.login'))

    doc = query_db("SELECT * FROM documents WHERE id = ?", (doc_id,), one=True)
    if not doc:
        flash("Document not found.", "danger")
        return redirect(url_for('citizen_dashboard'))

    if session.get('role') != 'admin' and doc['user_id'] != session.get('user_id'):
        flash("Unauthorized access to this document.", "danger")
        return redirect(url_for('citizen_dashboard'))

    filename = os.path.basename(doc['file_path'])
    as_attachment = request.args.get('download') == '1'

    return send_from_directory(
        Config.UPLOAD_FOLDER,
        filename,
        as_attachment=as_attachment,
        download_name=doc['file_name'] if as_attachment else None
    )