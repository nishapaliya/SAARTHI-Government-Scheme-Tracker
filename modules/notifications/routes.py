from flask import Blueprint, jsonify, session
from database.db import query_db, execute_db

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/api/list')
def get_user_notifications():
    if 'user_id' not in session:
        return jsonify([])
        
    notifications = query_db("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 10", (session['user_id'],))
    return jsonify(notifications)

@notifications_bp.route('/api/mark-read/<int:notif_id>', methods=['POST'])
def mark_read(notif_id):
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
        
    execute_db("UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?", (notif_id, session['user_id']))
    return jsonify({'success': True})
