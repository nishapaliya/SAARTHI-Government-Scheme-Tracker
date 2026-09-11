import os
import pytest
import sys

# Ensure app root is in import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database.db import init_db, query_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

def test_home_page(client):
    """Test public home page rendering."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"SAARTHI" in rv.data
    assert b"1.4 Billion Citizens" in rv.data

def test_schemes_catalog(client):
    """Test scheme directory listing."""
    rv = client.get('/schemes/')
    assert rv.status_code == 200
    assert b"Pradhan Mantri" in rv.data or b"Kisan" in rv.data

def test_eligibility_checker_api(client):
    """Test scheme eligibility calculator JSON API."""
    rv = client.post('/schemes/api/check-eligibility', json={
        'age': 25,
        'income': 150000,
        'gender': 'Male',
        'category': 'OBC',
        'occupation': 'Farmer'
    })
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'eligible_schemes' in data
    assert data['matched_count'] > 0

def test_chatbot_query(client):
    """Test rule-based AI chatbot assistant."""
    rv = client.post('/chatbot/query', json={'message': 'PM Kisan eligibility'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'Pradhan Mantri Kisan Samman Nidhi' in data['reply']

def test_admin_access_unauthorized(client):
    """Test security constraint for unauthenticated user accessing admin portal."""
    rv = client.get('/admin/dashboard', follow_redirects=True)
    assert b"Admin credentials required" in rv.data or b"Sign In" in rv.data
