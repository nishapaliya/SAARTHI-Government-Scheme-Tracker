import calendar
from flask import Blueprint, jsonify, session
from database.db import query_db

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

# Statuses that count as "successfully cleared" across every dashboard metric.
# NOTE: the live application workflow (see modules/applications/routes.py)
# only ever sets status to 'approved' or 'disbursement_in_progress' - 'disbursed'
# is kept here for forward-compatibility in case that status value is ever used.
SUCCESS_STATUSES = ('approved', 'disbursement_in_progress', 'disbursed')
SUCCESS_STATUS_PLACEHOLDERS = ','.join(['?'] * len(SUCCESS_STATUSES))


@analytics_bp.route('/api/kpis')
def get_kpis():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    total_apps = query_db("SELECT COUNT(*) as count FROM applications", one=True)['count']
    pending_apps = query_db(
        "SELECT COUNT(*) as count FROM applications WHERE status IN ('submitted', 'under_scrutiny', 'field_verification')",
        one=True
    )['count']
    approved_apps = query_db(
        f"SELECT COUNT(*) as count FROM applications WHERE status IN ({SUCCESS_STATUS_PLACEHOLDERS})",
        SUCCESS_STATUSES, one=True
    )['count']
    total_dbt = query_db("SELECT SUM(disbursed_amount) as total FROM applications", one=True)['total'] or 0.0
    rejected_apps = query_db("SELECT COUNT(*) as count FROM applications WHERE status = 'rejected'", one=True)['count']

    total_citizens = query_db("SELECT COUNT(*) as count FROM users WHERE role = 'citizen'", one=True)['count']
    total_schemes = query_db("SELECT COUNT(*) as count FROM schemes WHERE status = 'active'", one=True)['count']

    return jsonify({
        'total_applications': total_apps,
        'pending_scrutiny': pending_apps,
        'approved_disbursed': approved_apps,
        'rejected': rejected_apps,
        'total_dbt_amount': total_dbt,
        'total_citizens': total_citizens,
        'active_schemes': total_schemes,
        'settlement_rate': round((approved_apps / (total_apps or 1)) * 100, 1)
    })


@analytics_bp.route('/api/sector-approved-applications')
def sector_approved_applications():
    """
    Chart.js Doughnut: Sector-Wise Approved Applications.
    Counts approved/disbursed applications grouped by scheme category.
    """
    data = query_db(f'''
        SELECT s.category, COUNT(*) as total
        FROM applications a
        JOIN schemes s ON a.scheme_id = s.id
        WHERE a.status IN ({SUCCESS_STATUS_PLACEHOLDERS})
        GROUP BY s.category
        ORDER BY total DESC
    ''', SUCCESS_STATUSES)

    labels = [d['category'] for d in data]
    counts = [d['total'] for d in data]

    return jsonify({
        'labels': labels,
        'counts': counts
    })


@analytics_bp.route('/api/monthly-trends')
def monthly_trends():
    """
    Chart.js Line: Submitted vs Approved vs Disbursed, grouped by month
    from the actual applied_date / approval_date / disbursement_date columns.
    """
    submitted_rows = query_db('''
        SELECT YEAR(applied_date) as yr, MONTH(applied_date) as mo, COUNT(*) as cnt
        FROM applications
        WHERE applied_date IS NOT NULL
        GROUP BY YEAR(applied_date), MONTH(applied_date)
    ''')
    approved_rows = query_db('''
        SELECT YEAR(approval_date) as yr, MONTH(approval_date) as mo, COUNT(*) as cnt
        FROM applications
        WHERE approval_date IS NOT NULL
        GROUP BY YEAR(approval_date), MONTH(approval_date)
    ''')
    disbursed_rows = query_db('''
        SELECT YEAR(disbursement_date) as yr, MONTH(disbursement_date) as mo, COUNT(*) as cnt
        FROM applications
        WHERE disbursement_date IS NOT NULL
        GROUP BY YEAR(disbursement_date), MONTH(disbursement_date)
    ''')

    def to_map(rows):
        return {(r['yr'], r['mo']): r['cnt'] for r in rows}

    submitted_map = to_map(submitted_rows)
    approved_map = to_map(approved_rows)
    disbursed_map = to_map(disbursed_rows)

    # Union of every (year, month) that appears in any of the three series,
    # sorted chronologically, so the three lines always share the same x-axis.
    all_keys = sorted(set(submitted_map) | set(approved_map) | set(disbursed_map))

    months = [f"{calendar.month_abbr[mo]} {yr}" for (yr, mo) in all_keys]
    submitted = [submitted_map.get(k, 0) for k in all_keys]
    approved = [approved_map.get(k, 0) for k in all_keys]
    disbursed = [disbursed_map.get(k, 0) for k in all_keys]

    return jsonify({
        'months': months,
        'submitted': submitted,
        'approved': approved,
        'disbursed': disbursed
    })


@analytics_bp.route('/api/district-clearance')
def district_clearance():
    """
    Chart.js Bar: District-wise clearance efficiency.
    clearance % = (approved + disbursement_in_progress + disbursed) / total applications * 100, per district.

    Every district with at least one application appears here - including
    districts at 0% clearance. Nothing is filtered out by rate.
    """
    # TRIM() normalizes accidental leading/trailing whitespace in u.district
    # (e.g. "Mumbai" vs "Mumbai " would otherwise split into two separate bars).
    # This does NOT merge genuinely different district names like
    # "Mumbai" vs "Mumbai City" vs "Mumbai Suburban" - those are distinct
    # districts and are expected to appear as separate bars unless your
    # seed/user data should be corrected to use one consistent name.
    data = query_db(f'''
        SELECT TRIM(u.district) as district,
               COUNT(*) as total,
               SUM(CASE WHEN a.status IN ({SUCCESS_STATUS_PLACEHOLDERS}) THEN 1 ELSE 0 END) as cleared
        FROM applications a
        JOIN users u ON a.user_id = u.id
        WHERE u.district IS NOT NULL AND TRIM(u.district) <> ''
        GROUP BY TRIM(u.district)
        ORDER BY total DESC
    ''', SUCCESS_STATUSES)

    districts = [d['district'] for d in data]
    clearance_rate = [
        round((d['cleared'] / d['total']) * 100, 1) if d['total'] else 0.0
        for d in data
    ]

    # --- Debug logging so Mumbai (or any district) can be verified directly
    # in the server console. Remove or lower to logging.debug once confirmed. ---
    print("=" * 60)
    print("[district-clearance] Raw SQL result:")
    for d in data:
        rate = round((d['cleared'] / d['total']) * 100, 1) if d['total'] else 0.0
        print(f"  district={d['district']!r}  total={d['total']}  cleared={d['cleared']}  rate={rate}%")
    mumbai_rows = [d for d in data if 'mumbai' in (d['district'] or '').lower()]
    if mumbai_rows:
        print(f"[district-clearance] Mumbai-matching rows found: {mumbai_rows}")
    else:
        print("[district-clearance] WARNING: No district containing 'mumbai' found in query result.")
    print("=" * 60)

    return jsonify({
        'districts': districts,
        'clearance_rate': clearance_rate
    })