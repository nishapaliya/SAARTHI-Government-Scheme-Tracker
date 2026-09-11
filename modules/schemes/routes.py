from flask import Blueprint, render_template, request, jsonify
from database.db import query_db

schemes_bp = Blueprint('schemes', __name__, url_prefix='/schemes')

@schemes_bp.route('/')
def list_schemes():
    category_filter = request.args.get('category', 'All')
    search_q = request.args.get('q', '').strip()
    
    query = "SELECT * FROM schemes WHERE status = 'active'"
    params = []
    
    if category_filter != 'All':
        query += " AND category = ?"
        params.append(category_filter)
        
    if search_q:
        query += " AND (title LIKE ? OR ministry LIKE ? OR description LIKE ?)"
        params.extend([f"%{search_q}%", f"%{search_q}%", f"%{search_q}%"])
        
    query += " ORDER BY id ASC"
    schemes = query_db(query, tuple(params))
    
    categories = query_db("SELECT DISTINCT category FROM schemes WHERE status = 'active'")
    category_list = [c['category'] for c in categories]
    
    return render_template('schemes/index.html', schemes=schemes, categories=category_list, selected_category=category_filter, search_q=search_q)

@schemes_bp.route('/<int:scheme_id>')
def scheme_detail(scheme_id):
    scheme = query_db("SELECT * FROM schemes WHERE id = ?", (scheme_id,), one=True)
    if not scheme:
        return "Scheme Not Found", 404
    return render_template('schemes/detail.html', scheme=scheme)

@schemes_bp.route('/api/search')
def api_search_schemes():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])
        
    schemes = query_db('''
    SELECT id, code, title, ministry, category, benefit_amount 
    FROM schemes 
    WHERE status = 'active' AND (title LIKE ? OR code LIKE ? OR category LIKE ? OR ministry LIKE ?)
    LIMIT 8
    ''', (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"))
    return jsonify(schemes)

@schemes_bp.route('/api/check-eligibility', methods=['POST'])
def check_eligibility():
    """Matches user parameters against scheme conditions and returns qualified schemes."""
    data = request.get_json() or {}
    age = int(data.get('age', 25))
    income = float(data.get('income', 200000))
    gender = data.get('gender', 'All')
    category = data.get('category', 'All')
    occupation = data.get('occupation', 'All')
    
    all_schemes = query_db("SELECT * FROM schemes WHERE status = 'active'")
    eligible = []
    
    for s in all_schemes:
        match = True
        
        # Age criteria
        if not (s['eligibility_min_age'] <= age <= s['eligibility_max_age']):
            match = False
            
        # Income criteria
        if income > s['eligibility_max_income']:
            match = False
            
        # Gender criteria
        if s['gender_target'] != 'All' and gender != 'All' and s['gender_target'] != gender:
            match = False
            
        # Category criteria
        if s['target_category'] != 'All' and category != 'All':
            allowed_cats = [c.strip() for c in s['target_category'].split(',')]
            if category not in allowed_cats and 'All' not in allowed_cats:
                match = False
                
        # Occupation criteria
        if s['target_occupation'] != 'All' and occupation != 'All' and s['target_occupation'].lower() not in occupation.lower():
            match = False
            
        if match:
            eligible.append(s)
            
    return jsonify({
        'total_checked': len(all_schemes),
        'matched_count': len(eligible),
        'eligible_schemes': eligible
    })
