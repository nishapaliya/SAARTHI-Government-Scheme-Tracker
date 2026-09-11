from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database.db import query_db, execute_db

reminders_bp = Blueprint('reminders', __name__, url_prefix='/reminders')

@reminders_bp.route('/')
def list_reminders():
    if 'user_id' not in session:
        flash("Login required to view reminders.", "warning")
        return redirect(url_for('auth.login'))
        
    reminders = query_db("SELECT * FROM reminders WHERE user_id = ? ORDER BY due_date ASC", (session['user_id'],))
    return render_template('citizen/reminders.html', reminders=reminders)

@reminders_bp.route('/add', methods=['POST'])
def add_reminder():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    title = request.form.get('title', '').strip()
    due_date = request.form.get('due_date', '')
    reminder_type = request.form.get('reminder_type', 'disbursement')
    description = request.form.get('description', '')
    
    if not title or not due_date:
        return jsonify({'success': False, 'message': 'Title and Due Date required.'}), 400
        
    rem_id = execute_db('''
    INSERT INTO reminders (user_id, title, due_date, reminder_type, description)
    VALUES (?, ?, ?, ?, ?)
    ''', (session['user_id'], title, due_date, reminder_type, description))
    
    return jsonify({'success': True, 'message': 'Reminder added.', 'id': rem_id})

@reminders_bp.route('/toggle/<int:rem_id>', methods=['POST'])
def toggle_reminder(rem_id):
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
        
    rem = query_db("SELECT is_completed FROM reminders WHERE id = ? AND user_id = ?", (rem_id, session['user_id']), one=True)
    if rem:
        new_val = 0 if rem['is_completed'] else 1
        execute_db("UPDATE reminders SET is_completed = ? WHERE id = ?", (new_val, rem_id))
        return jsonify({'success': True, 'is_completed': new_val})
        
    return jsonify({'success': False}), 44
