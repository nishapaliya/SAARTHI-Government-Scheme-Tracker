/* Global Client JS - SAARTHI Portal */

// 1. Accessibility Font Resizer
let currentFontSizeOffset = 0;
function changeFontSize(delta) {
    currentFontSizeOffset += delta;
    if(currentFontSizeOffset > 3) currentFontSizeOffset = 3;
    if(currentFontSizeOffset < -2) currentFontSizeOffset = -2;
    document.body.style.fontSize = (16 + currentFontSizeOffset) + 'px';
    localStorage.setItem('saarthi_font_offset', currentFontSizeOffset);
}
function resetFontSize() {
    currentFontSizeOffset = 0;
    document.body.style.fontSize = '16px';
    localStorage.setItem('saarthi_font_offset', 0);
}

// 2. High Contrast Mode Toggle
function toggleContrast() {
    document.body.classList.toggle('high-contrast');
    const isContrast = document.body.classList.contains('high-contrast');
    localStorage.setItem('saarthi_high_contrast', isContrast ? 'true' : 'false');
}

// Restore accessibility preferences on load
document.addEventListener('DOMContentLoaded', () => {
    const savedFont = localStorage.getItem('saarthi_font_offset');
    if(savedFont) {
        currentFontSizeOffset = parseInt(savedFont);
        document.body.style.fontSize = (16 + currentFontSizeOffset) + 'px';
    }
    if(localStorage.getItem('saarthi_high_contrast') === 'true') {
        document.body.classList.add('high-contrast');
    }
    
    // Header search autocomplete setup
    const searchInput = document.getElementById('headerSearchInput');
    if(searchInput) {
        searchInput.addEventListener('input', handleHeaderSearchInput);
    }

    // Load unread notifications
    loadNotifications();
});

// 3. Header Search Autocomplete
function handleHeaderSearchInput(e) {
    const q = e.target.value.trim();
    const dropdown = document.getElementById('searchAutocompleteList');
    if(!dropdown) return;

    if(q.length < 2) {
        dropdown.style.display = 'none';
        return;
    }

    fetch('/schemes/api/search?q=' + encodeURIComponent(q))
    .then(r => r.json())
    .then(data => {
        if(data.length === 0) {
            dropdown.innerHTML = '<div class="p-3 text-muted fs-8">No schemes found matching query.</div>';
        } else {
            let html = '';
            data.forEach(item => {
                html += `
                <a href="/schemes/${item.id}" class="dropdown-item p-2 border-bottom text-decoration-none">
                    <div class="fw-bold font-outfit text-primary-blue fs-7">${item.title}</div>
                    <div class="fs-8 text-muted">${item.category} • ₹${item.benefit_amount.toLocaleString()}</div>
                </a>`;
            });
            dropdown.innerHTML = html;
        }
        dropdown.style.display = 'block';
    });
}

function handleHeaderSearch(e) {
    e.preventDefault();
    const q = document.getElementById('headerSearchInput').value.trim();
    if(q) {
        window.location.href = '/schemes/?q=' + encodeURIComponent(q);
    }
}

// 4. Interactive Eligibility Finder Quiz
function runEligibilityCheck() {
    const age = document.getElementById('age').value;
    const income = document.getElementById('income').value;
    const gender = document.getElementById('gender').value;
    const category = document.getElementById('category').value;
    const occupation = document.getElementById('occupation').value;

    const resultsContainer = document.getElementById('eligibilityResults');
    resultsContainer.style.display = 'block';
    resultsContainer.innerHTML = '<div class="text-center py-4 text-muted"><i class="fa-solid fa-spinner fa-spin me-2"></i> Analyzing demographic criteria against 500+ scheme rules...</div>';

    fetch('/schemes/api/check-eligibility', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ age, income, gender, category, occupation })
    })
    .then(r => r.json())
    .then(data => {
        if(data.matched_count === 0) {
            resultsContainer.innerHTML = `
            <div class="alert alert-warning border-0 rounded-4 p-4 text-center">
                <i class="fa-solid fa-circle-exclamation fs-2 text-warning mb-2"></i>
                <h5 class="font-outfit fw-bold text-dark mb-1">No Direct Matching Schemes</h5>
                <p class="fs-7 text-muted mb-0">Try adjusting your age or annual income filters to see general central welfare schemes.</p>
            </div>`;
        } else {
            let html = `
            <div class="alert alert-success border-0 rounded-4 p-3 mb-4 d-flex align-items-center justify-content-between">
                <div><i class="fa-solid fa-circle-check me-2"></i> <strong>Matched ${data.matched_count} Government Schemes</strong> for your demographic profile!</div>
                <span class="badge bg-white text-success fs-8">100% Aadhaar Verified Rules</span>
            </div>
            <div class="row g-3">`;

            data.eligible_schemes.forEach(s => {
                html += `
                <div class="col-md-6">
                    <div class="card bg-white border-0 rounded-4 p-3 shadow-sm hover-elevate">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge bg-blue-subtle text-primary-blue fs-9">${s.category}</span>
                            <span class="font-outfit fw-extrabold text-success fs-6">₹${s.benefit_amount.toLocaleString()}</span>
                        </div>
                        <h6 class="font-outfit fw-bold text-dark mb-1">${s.title}</h6>
                        <p class="fs-8 text-muted line-clamp-2 mb-3">${s.description}</p>
                        <a href="/applications/wizard/${s.id}" class="btn btn-sm btn-primary-gradient rounded-pill text-white w-100 font-outfit fw-bold">
                            Apply Now (5-Step Wizard) <i class="fa-solid fa-arrow-right ms-1"></i>
                        </a>
                    </div>
                </div>`;
            });
            html += '</div>';
            resultsContainer.innerHTML = html;
        }
    });
}

// 5. Notifications Fetcher
function loadNotifications() {
    const listEl = document.getElementById('notificationList');
    if(!listEl) return;

    fetch('/notifications/api/list')
    .then(r => r.json())
    .then(data => {
        if(data.length === 0) {
            listEl.innerHTML = '<div class="text-center text-muted py-3 fs-8">No notifications received yet.</div>';
        } else {
            let html = '';
            data.forEach(item => {
                html += `
                <div class="p-2 border-bottom fs-8">
                    <div class="fw-bold text-primary-blue">${item.title}</div>
                    <div class="text-muted fs-9">${item.message}</div>
                </div>`;
            });
            listEl.innerHTML = html;
        }
    });
}

// 6. Aadhaar e-KYC Simulation Function
function simulateEKYC() {
    const aadhaarInput = document.getElementById('regAadhaar');
    const badge = document.getElementById('ekycBadge');
    if(!aadhaarInput) return;

    const val = aadhaarInput.value.trim();
    if(val.length !== 12 || !/^\d+$/.test(val)) {
        badge.style.display = 'block';
        badge.className = 'fs-8 mt-2 text-danger font-outfit fw-bold';
        badge.innerHTML = '<i class="fa-solid fa-circle-xmark me-1"></i> Please enter a valid 12-digit numeric Aadhaar number.';
        return;
    }

    badge.style.display = 'block';
    badge.className = 'fs-8 mt-2 text-primary font-outfit fw-bold';
    badge.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i> Contacting UIDAI Central Identities Data Repository...';

    fetch('/auth/api/ekyc-verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ aadhaar_no: val })
    })
    .then(r => r.json())
    .then(data => {
        if(data.success) {
            badge.className = 'fs-8 mt-2 text-success font-outfit fw-bold';
            badge.innerHTML = `<i class="fa-solid fa-circle-check me-1"></i> ${data.message} (${data.details.state} Address Verified)`;
        } else {
            badge.className = 'fs-8 mt-2 text-danger font-outfit fw-bold';
            badge.innerHTML = `<i class="fa-solid fa-circle-xmark me-1"></i> ${data.message}`;
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {

    const savedFont = localStorage.getItem('saarthi_font_offset');
    if(savedFont){
        currentFontSizeOffset = parseInt(savedFont);
        document.body.style.fontSize = (16 + currentFontSizeOffset) + 'px';
    }

    if(localStorage.getItem('saarthi_high_contrast') === 'true'){
        document.body.classList.add('high-contrast');
    }

    const searchInput = document.getElementById('headerSearchInput');
    if(searchInput){
        searchInput.addEventListener('input', handleHeaderSearchInput);
    }

    loadNotifications();

    // ===============================
    // Live Statistics Counter
    // ===============================

    document.querySelectorAll('.counter').forEach(counter => {

        const updateCounter = () => {

            const target = +counter.getAttribute('data-target');
            const current = +counter.innerText.replace(/,/g,'');

            const increment = target / 120;

            if(current < target){

                counter.innerText = Math.ceil(current + increment).toLocaleString();

                setTimeout(updateCounter,15);

            }else{

                counter.innerText = target.toLocaleString();

            }

        };

        updateCounter();

    });

    // ===============================
// FAQ Search
// ===============================

const faqSearch = document.getElementById("faqSearch");

if (faqSearch) {

    faqSearch.addEventListener("keyup", function () {

        const value = this.value.toLowerCase();

        document.querySelectorAll(".faq-item").forEach(item => {

            if (item.innerText.toLowerCase().includes(value)) {

                item.style.display = "block";

            } else {

                item.style.display = "none";

            }

        });

    });

}

});
// ===============================
// Homepage Analytics Charts
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    if(document.getElementById("applicationsChart")){

        new Chart(document.getElementById("applicationsChart"),{

            type:"line",

            data:{
                labels:["Jan","Feb","Mar","Apr","May","Jun"],
                datasets:[{
                    label:"Applications",
                    data:[120,180,240,300,420,510],
                    borderColor:"#0d6efd",
                    backgroundColor:"rgba(13,110,253,.15)",
                    tension:.4,
                    fill:true
                }]
            }

        });

        new Chart(document.getElementById("statusChart"),{

            type:"doughnut",

            data:{
                labels:["Approved","Pending","Rejected"],
                datasets:[{
                    data:[65,25,10]
                }]
            }

        });

        new Chart(document.getElementById("categoryChart"),{

            type:"bar",

            data:{
                labels:["Education","Health","Housing","Agriculture","Women"],

                datasets:[{
                    label:"Schemes",
                    data:[50,42,35,28,31]
                }]
            }

        });

        new Chart(document.getElementById("benefitChart"),{

            type:"pie",

            data:{
                labels:["Scholarships","Subsidy","Pension","Insurance"],

                datasets:[{
                    data:[35,30,20,15]
                }]
            }

        });

    }

});

 document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("checkEligibilityBtn");

    if (btn) {
        btn.addEventListener("click", runEligibilityCheck);
    }
});


/* ======================================
   MORE MENU SUBMENU
====================================== */

document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".dropend").forEach(function (dropdown) {

        dropdown.addEventListener("mouseenter", function () {

            let submenu = dropdown.querySelector(".dropdown-menu");

            submenu.classList.add("show");

        });

        dropdown.addEventListener("mouseleave", function () {

            let submenu = dropdown.querySelector(".dropdown-menu");

            submenu.classList.remove("show");

        });

    });

});