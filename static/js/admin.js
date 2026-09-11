/* Nodal Officer Admin Portal JS - Chart.js & Approval Handler */

document.addEventListener('DOMContentLoaded', () => {
    loadAdminKpis();
    initSectorChart();
    initTrendChart();
    initDistrictChart();
});

// 1. Fetch & Render KPI Metrics
function loadAdminKpis() {
    fetch('/analytics/api/kpis')
    .then(r => r.json())
    .then(data => {
        if(document.getElementById('kpiPendingApps')) {
            document.getElementById('kpiPendingApps').innerText = data.pending_scrutiny;
        }
        if(document.getElementById('kpiTotalDbt')) {
            document.getElementById('kpiTotalDbt').innerText = '₹' + data.total_dbt_amount.toLocaleString();
        }
        if(document.getElementById('kpiSettlementRate')) {
            document.getElementById('kpiSettlementRate').innerText = data.settlement_rate + '%';
        }
    });
}

// 2. Chart.js Sector-Wise Approved Applications Doughnut Chart
function initSectorChart() {
    const ctx = document.getElementById('sectorChart');
    if(!ctx) return;

    fetch('/analytics/api/sector-approved-applications')
    .then(r => r.json())
    .then(data => {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.counts,
                    backgroundColor: ['#1565C0', '#2E7D32', '#FB8C00', '#D32F2F', '#9C27B0', '#00ACC1', '#6D4C41', '#546E7A'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                }
            }
        });
    });
}

// 3. Chart.js Monthly Trends Line Chart
function initTrendChart() {
    const ctx = document.getElementById('trendChart');
    if(!ctx) return;

    fetch('/analytics/api/monthly-trends')
    .then(r => r.json())
    .then(data => {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.months,
                datasets: [
                    { label: 'Submitted', data: data.submitted, borderColor: '#1565C0', tension: 0.3, fill: false },
                    { label: 'Approved', data: data.approved, borderColor: '#FB8C00', tension: 0.3, fill: false },
                    { label: 'Disbursed', data: data.disbursed, borderColor: '#2E7D32', tension: 0.3, fill: false }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } } }
            }
        });
    });
}

// 4. Chart.js District Clearance Bar Chart
function initDistrictChart() {
    const ctx = document.getElementById('districtChart');
    if(!ctx) return;

    fetch('/analytics/api/district-clearance')
    .then(r => r.json())
    .then(data => {
        // Debug: verify Mumbai (or any district) is present in the payload
        // before Chart.js ever touches it. Check the browser console.
        console.log('[district-clearance] API payload:', data);
        const mumbaiIndex = data.districts.findIndex(d => d.toLowerCase().includes('mumbai'));
        if (mumbaiIndex !== -1) {
            console.log(`[district-clearance] Mumbai found at index ${mumbaiIndex}: ${data.clearance_rate[mumbaiIndex]}%`);
        } else {
            console.warn('[district-clearance] No district containing "mumbai" in API response.');
        }

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.districts,
                datasets: [{
                    label: 'Clearance %',
                    data: data.clearance_rate,
                    backgroundColor: 'rgba(21, 101, 192, 0.85)',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                // FIX: min was 80, which clipped/hid any district below 80%
                // clearance (e.g. Mumbai). 0-100 shows every district's real value.
                scales: { y: { min: 0, max: 100 } }
            }
        });
    });
}

// 5. Trigger Status Updates & Simulated Direct Benefit Transfer (DBT)
// Friendly display labels so prompts/alerts match the badge text shown in the table
// (e.g. 'disbursement_in_progress' status displays as "Forwarded to Government" everywhere).
const STATUS_DISPLAY_LABELS = {
    'under_scrutiny': 'Under Scrutiny',
    'field_verification': 'Field Verification',
    'approved': 'Approved',
    'disbursement_in_progress': 'Forwarded to Government',
    'rejected': 'Rejected'
};

function triggerStatusUpdate(appId, newStatus) {
    const label = STATUS_DISPLAY_LABELS[newStatus] || newStatus.replace(/_/g, ' ').toUpperCase();
    let remarks = prompt(`Updating Application #${appId} to status "${label}". Enter audit remarks:`, 'Verified by Nodal Scrutiny Committee.');
    if(remarks === null) return;

    fetch('/applications/api/status-update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            app_id: appId,
            status: newStatus,
            remarks: remarks
        })
    })
    .then(r => r.json())
    .then(data => {
        if(data.success) {
            alert('✅ ' + data.message);
            location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    });
}

function promptRejectModal(appId) {
    let reason = prompt(`Rejection Reason for Application #${appId}:`, 'Income certificate threshold exceeded.');
    if(!reason) return;

    fetch('/applications/api/status-update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            app_id: appId,
            status: 'rejected',
            rejection_reason: reason
        })
    })
    .then(r => r.json())
    .then(data => {
        if(data.success) {
            alert('Application status updated to REJECTED.');
            location.reload();
        }
    });
}