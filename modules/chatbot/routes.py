from ai.groq_client import ask_ai

from flask import Blueprint, request, jsonify
from database.db import query_db
from dotenv import load_dotenv
load_dotenv()



chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/query', methods=['POST'])
def query():
    data = request.get_json() or {}
    message = data.get('message', '').strip().lower()
    
    if not message:
        return jsonify({'reply': 'Namaste! I am SAARTHI AI Assistant. How can I help you today? You can ask about schemes, eligibility, DBT status, or required documents.'})
        
    # Rule 1: Application Tracker Query
    if 'srt-' in message or 'status' in message or 'track' in message:
        # Check if a reference number is given
        words = message.split()
        ref = None
        for w in words:
            if 'srt-' in w:
                ref = w.upper()
                break
                
        if ref:
            app_data = query_db("SELECT a.*, s.title FROM applications a JOIN schemes s ON a.scheme_id = s.id WHERE a.application_ref = %s", (ref,), one=True)
            if app_data:
                return jsonify({'reply': f"📌 Application {ref} ({app_data['title']}): Current Status is **{app_data['status'].replace('_', ' ').upper()}**. Applied on: {app_data['applied_date']}."})
            else:
                return jsonify({'reply': f"❌ No application found matching Reference Number {ref}. Please check the number and try again."})
        return jsonify({'reply': "To track your application, please provide your Application Reference Number (e.g. `SRT-2026-98124`)."})
        
    
    # Rule 8 : AI Fallback

    try:
        ai_reply = ask_ai(message)

        return jsonify({
            "reply": ai_reply
        })

    except Exception:

     return jsonify({
        "reply":"Sorry, AI service is temporarily unavailable."
    })