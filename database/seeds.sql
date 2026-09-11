

-- ============================================================
-- SAARTHI: Initial Seed Data for Schemes, Users, & Applications
-- Expanded to 20 real Indian Government Schemes
-- ============================================================
 
USE saarthi_db;
 
-- Passwords: 
-- admin123 -> pbkdf2:sha256:600000$saarthi$b04856f6630f56a6839352ef2e12e12e12e12e12e12e12e12e12e12e12e12e12
-- citizen123 -> pbkdf2:sha256:600000$saarthi$c1234567890abcdef1234567890abcdef1234567890abcdef1234567890abc
-- (Our db.py will generate runtime hashes if needed)
 
-- 1. Users
INSERT INTO users (id, aadhaar_no, full_name, email, mobile, password_hash, role, dob, gender, category, income_annual, occupation, state, district, dbt_bank_account, ifsc_code, bank_name) VALUES
(1, '999988887777', 'Rajesh Verma (Nodal Officer)', 'admin@saarthi.gov.in', '9876543210', 'pbkdf2:sha256:260000$uGg2Wq4L$883b63297a73a3f5b746fb9f3301a52e9f0d11bf4c6e94a821e25e0bc87cfd67', 'admin', '1980-05-15', 'Male', 'General', 1200000.00, 'Government Service', 'Delhi', 'New Delhi', '918273645019', 'SBIN0001001', 'State Bank of India'),
(2, '234567890123', 'Ramesh Kumar Patel', 'ramesh.patel@gmail.com', '9812345678', 'pbkdf2:sha256:260000$uGg2Wq4L$883b63297a73a3f5b746fb9f3301a52e9f0d11bf4c6e94a821e25e0bc87cfd67', 'citizen', '1988-08-20', 'Male', 'OBC', 180000.00, 'Farmer', 'Uttar Pradesh', 'Varanasi', '501002349182', 'HDFC0000123', 'HDFC Bank'),
(3, '345678901234', 'Priya Sharma', 'priya.sharma@gmail.com', '9876512345', 'pbkdf2:sha256:260000$uGg2Wq4L$883b63297a73a3f5b746fb9f3301a52e9f0d11bf4c6e94a821e25e0bc87cfd67', 'citizen', '1995-12-10', 'Female', 'General', 240000.00, 'Entrepreneur', 'Maharashtra', 'Pune', '309281746501', 'ICIC0000999', 'ICICI Bank'),
(4, '456789012345', 'Sunita Devi', 'sunita.devi@gmail.com', '9823456789', 'pbkdf2:sha256:260000$uGg2Wq4L$883b63297a73a3f5b746fb9f3301a52e9f0d11bf4c6e94a821e25e0bc87cfd67', 'citizen', '1990-03-25', 'Female', 'SC', 95000.00, 'Artisan', 'Bihar', 'Patna', '601293847561', 'PUNB0000555', 'Punjab National Bank');
 
-- 2. Schemes (20 total: 7 original + 13 new)
-- NOTE: categories below are normalized to exactly match the 8 homepage
-- category filters: Agriculture, Housing, Healthcare, Education, Women,
-- Employment, Pension, Entrepreneurship.
INSERT INTO schemes (id, code, title, ministry, category, benefit_amount, benefit_type, eligibility_min_age, eligibility_max_age, eligibility_max_income, gender_target, target_category, target_occupation, description, benefits_summary, documents_required, deadline, status) VALUES
 
-- Existing 7 (categories 6 and 7 corrected to match homepage filters)
(1, 'PM-KISAN', 'Pradhan Mantri Kisan Samman Nidhi', 'Ministry of Agriculture & Farmers Welfare', 'Agriculture', 6000.00, 'Direct Benefit Transfer (DBT)', 18, 80, 400000.00, 'All', 'All', 'Farmer', 'Financial assistance of the amount given below per year provided to all landholding farmer families across India in three equal installments.', 'Rs. 6,000/year credited directly into bank account in 3 installments of Rs. 2,000.', 'Aadhaar Card, Land Holding Certificate, Bank Passbook', '2026-12-31', 'active'),
(2, 'PMAY-U', 'Pradhan Mantri Awas Yojana (Urban)', 'Ministry of Housing and Urban Affairs', 'Housing', 250000.00, 'Interest Subsidy / Capital Grant', 21, 70, 300000.00, 'All', 'All', 'All', 'Affordable housing subsidy for Economically Weaker Section (EWS) and Low Income Group (LIG) families building or purchasing their first pucca home.', 'Financial assistance up to Rs. 2.5 Lakh for house construction/renovation.', 'Aadhaar Card, Income Certificate, Property Documents, Bank Passbook', '2026-11-30', 'active'),
(3, 'PM-ABPMJAY', 'Ayushman Bharat - PM Jan Arogya Yojana', 'Ministry of Health and Family Welfare', 'Healthcare', 500000.00, 'Cashless Health Insurance Cover', 0, 100, 250000.00, 'All', 'All', 'All', 'World largest government-funded healthcare scheme providing cashless coverage of up to Rs. 5 Lakh per family per year for secondary and tertiary care hospitalization.', 'Cashless hospital cover up to Rs. 5,00,000 at 28,000+ empaneled hospitals.', 'Aadhaar Card, Ration Card / SECC 2011 proof', '2027-03-31', 'active'),
(4, 'PM-MUDRA', 'Pradhan Mantri MUDRA Yojana (Tarun)', 'Ministry of Finance', 'Entrepreneurship', 1000000.00, 'Collateral-free Micro Loan', 18, 65, 1500000.00, 'All', 'All', 'Entrepreneur', 'Loans up to Rs. 10 Lakh to non-corporate, non-farm small/micro enterprises for setting up or expanding business operations.', 'Collateral-free business credit up to Rs. 10 Lakhs with subsidized interest rates.', 'Aadhaar Card, PAN Card, Business Plan Project Report, Bank Statement', '2026-10-15', 'active'),
(5, 'NSP-POSTMATRIC', 'National Post-Matric Scholarship Scheme', 'Ministry of Social Justice and Empowerment', 'Education', 45000.00, 'Academic Fee Subsidy + Maintenance', 15, 30, 250000.00, 'All', 'SC, ST, OBC', 'Student', 'Financial aid to meritorious students belonging to minority/reserved categories pursuing higher education post 10th grade.', 'Full tuition fee reimbursement + monthly stipend up to Rs. 45,000/year.', 'Aadhaar Card, Caste Certificate, Income Certificate, Previous Marksheets', '2026-09-30', 'active'),
(6, 'SSY-GIRL', 'Sukanya Samriddhi Yojana', 'Ministry of Women and Child Development', 'Women', 150000.00, 'High Interest Savings Benefit', 0, 10, 1000000.00, 'Female', 'All', 'All', 'Small deposit scheme for the girl child offering highest tax-free government interest rates (8.2%) to secure her future education and marriage.', 'Tax benefit under 80C + 8.2% annual interest compounded yearly.', 'Birth Certificate of Girl Child, Parents Aadhaar Card, Address Proof', '2027-12-31', 'active'),
(7, 'PM-SVANIDHI', 'PM Street Vendor AtmaNirbhar Nidhi', 'Ministry of Housing and Urban Affairs', 'Employment', 50000.00, 'Micro Credit Loan + Cashback', 18, 65, 300000.00, 'All', 'All', 'Street Vendor', 'Special micro-credit facility providing affordable collateral-free working capital loans up to Rs. 50,000 to street vendors affected by economic disruption.', 'Enhanced credit limit on timely repayment + 7% interest subsidy.', 'Aadhaar Card, Vending Certificate / ID Card, Bank Account', '2026-12-15', 'active'),
 
-- New: Agriculture (+2)
(8, 'PMFBY', 'Pradhan Mantri Fasal Bima Yojana', 'Ministry of Agriculture & Farmers Welfare', 'Agriculture', 200000.00, 'Crop Insurance Cover', 18, 70, 500000.00, 'All', 'All', 'Farmer', 'Low-premium crop insurance scheme protecting farmers against yield losses caused by natural calamities, pests and diseases across Kharif and Rabi seasons.', 'Comprehensive risk cover with farmer premium as low as 1.5% to 5% of the sum insured, balance subsidized by government.', 'Aadhaar Card, Land Records, Bank Passbook, Sowing Certificate', '2026-11-15', 'active'),
(9, 'PM-KSY', 'Pradhan Mantri Krishi Sinchayee Yojana', 'Ministry of Jal Shakti', 'Agriculture', 100000.00, 'Irrigation Infrastructure Subsidy', 18, 75, 400000.00, 'All', 'All', 'Farmer', 'Har Khet Ko Pani initiative ensuring assured irrigation and promoting water-use efficiency through micro-irrigation for every farm in the country.', 'Subsidy up to Rs. 1 Lakh per hectare for drip and sprinkler irrigation equipment.', 'Aadhaar Card, Land Holding Certificate, Water Source Proof', '2026-12-20', 'active'),
 
-- New: Housing (+2)
(10, 'PMAY-G', 'Pradhan Mantri Awas Yojana (Gramin)', 'Ministry of Rural Development', 'Housing', 130000.00, 'Housing Construction Assistance', 18, 100, 300000.00, 'All', 'All', 'All', 'Provides pucca houses with basic amenities to houseless and inadequately housed rural families identified through the SECC 2011 database.', 'Rs. 1.2 to 1.3 Lakh direct construction assistance plus 90/95 days of MGNREGA wage support for construction.', 'Aadhaar Card, SECC 2011 Proof, Bank Passbook, Land Ownership/Allotment Document', '2026-10-31', 'active'),
(11, 'PMAY-ARHC', 'Affordable Rental Housing Complexes', 'Ministry of Housing and Urban Affairs', 'Housing', 50000.00, 'Affordable Rental Housing Access', 18, 60, 300000.00, 'All', 'All', 'Migrant Worker', 'Converts government-funded vacant housing stock into affordable rental complexes to provide dignified living to urban migrant workers and the urban poor close to their workplace.', 'Subsidized rental housing units with basic amenities at concessional monthly rent.', 'Aadhaar Card, Employer/Employment Proof, Migration Certificate', '2026-09-30', 'active'),
 
-- New: Healthcare (+2)
(12, 'JSY', 'Janani Suraksha Yojana', 'Ministry of Health and Family Welfare', 'Healthcare', 1400.00, 'Maternity Cash Assistance', 19, 45, 250000.00, 'Female', 'All', 'All', 'Safe motherhood intervention promoting institutional delivery among pregnant women, particularly in low-performing states, to reduce maternal and infant mortality.', 'Cash assistance for institutional delivery plus free transport and postnatal care support.', 'Aadhaar Card, Pregnancy Registration Card, BPL Certificate (if applicable), Bank Passbook', '2027-01-31', 'active'),
(13, 'PMSBY', 'Pradhan Mantri Suraksha Bima Yojana', 'Ministry of Finance', 'Healthcare', 200000.00, 'Accidental Insurance Cover', 18, 70, 1000000.00, 'All', 'All', 'All', 'Affordable government-backed accident insurance scheme offering coverage for accidental death and disability at a nominal annual premium.', 'Rs. 2 Lakh cover on accidental death or full disability, Rs. 1 Lakh for partial disability, at a premium of only Rs. 20/year.', 'Aadhaar Card, Bank Account linked to Aadhaar', '2026-05-31', 'active'),
 
-- New: Education (+2)
(14, 'PM-YASASVI', 'PM Young Achievers Scholarship Award Scheme for Vibrant India', 'Ministry of Social Justice and Empowerment', 'Education', 125000.00, 'Merit Scholarship', 13, 20, 250000.00, 'All', 'OBC, EBC, DNT', 'Student', 'Financial support to meritorious students from OBC, EBC and DNT communities studying in classes 9 to 12 and top-ranked institutions.', 'Scholarship amount up to Rs. 1,25,000 per year depending on class and institution.', 'Aadhaar Card, Caste Certificate, Income Certificate, Previous Year Marksheet', '2026-08-31', 'active'),
(15, 'NMMSS', 'National Means-cum-Merit Scholarship Scheme', 'Ministry of Education', 'Education', 12000.00, 'Merit-cum-Means Scholarship', 13, 16, 350000.00, 'All', 'All', 'Student', 'Scholarship for economically weaker meritorious students to reduce the dropout rate at the transition from class 8 to class 9.', 'Rs. 12,000 per year (Rs. 1,000/month) for classes 9 through 12.', 'Aadhaar Card, Income Certificate, Class 8 Marksheet, Bank Passbook', '2026-11-30', 'active'),
 
-- New: Women (+1)
(16, 'PMMVY', 'Pradhan Mantri Matru Vandana Yojana', 'Ministry of Women and Child Development', 'Women', 5000.00, 'Maternity Benefit Cash Transfer', 19, 45, 800000.00, 'Female', 'All', 'All', 'Cash incentive for pregnant and lactating mothers for their first living child to partially compensate for wage loss and encourage better health and nutrition practices.', 'Rs. 5,000 paid in three installments directly to the bank account, in addition to Rs. 1,000 under JSY for institutional delivery.', 'Aadhaar Card, MCP Card, Bank Passbook, Husband Aadhaar Card', '2026-12-31', 'active'),
 
-- New: Employment (+1)
(17, 'MGNREGA', 'Mahatma Gandhi National Rural Employment Guarantee Act', 'Ministry of Rural Development', 'Employment', 24000.00, 'Guaranteed Wage Employment', 18, 60, 300000.00, 'All', 'All', 'Rural Laborer', 'Legal guarantee of 100 days of wage employment in a financial year to every rural household whose adult members volunteer to do unskilled manual work.', 'Guaranteed 100 days of wage employment per household per year at notified wage rates.', 'Aadhaar Card, Job Card, Bank Passbook', '2027-03-31', 'active'),
 
-- New: Pension (+2)
(18, 'APY', 'Atal Pension Yojana', 'Ministry of Finance', 'Pension', 60000.00, 'Guaranteed Monthly Pension', 18, 40, 1000000.00, 'All', 'All', 'All', 'Guaranteed minimum pension scheme for workers in the unorganized sector, providing a fixed monthly pension after age 60 based on the contribution slab chosen.', 'Guaranteed monthly pension of Rs. 1,000 to Rs. 5,000 after age 60, depending on contribution amount and age of joining.', 'Aadhaar Card, Bank Passbook, Mobile Number linked to Aadhaar', '2026-12-31', 'active'),
(19, 'PM-SYM', 'Pradhan Mantri Shram Yogi Maan-dhan', 'Ministry of Labour and Employment', 'Pension', 36000.00, 'Old Age Pension', 18, 40, 180000.00, 'All', 'All', 'Unorganized Sector Worker', 'Voluntary and contributory pension scheme for unorganized sector workers such as street vendors, rickshaw pullers and domestic workers, ensuring a monthly pension after age 60.', 'Minimum assured monthly pension of Rs. 3,000 after age 60 with matching government contribution.', 'Aadhaar Card, Bank Passbook, Income Self-Declaration', '2026-10-31', 'active'),
 
-- New: Entrepreneurship (+1)
(20, 'STANDUP-INDIA', 'Stand-Up India Scheme', 'Ministry of Finance', 'Entrepreneurship', 10000000.00, 'Bank Loan for Greenfield Enterprise', 18, 65, 2000000.00, 'All', 'SC, ST, Women', 'Entrepreneur', 'Facilitates bank loans between Rs. 10 Lakh and Rs. 1 Crore to at least one SC/ST borrower and one woman borrower per bank branch for setting up a greenfield enterprise.', 'Composite loan covering up to 75% of project cost for manufacturing, trading or services sector ventures.', 'Aadhaar Card, PAN Card, Business Project Report, Caste Certificate (if applicable), Bank Statement', '2026-11-15', 'active');
 
-- 3. Applications (original 5 + 8 new, covering the new schemes)
INSERT INTO applications (id, application_ref, user_id, scheme_id, status, applied_date, scrutiny_date, verification_date, approval_date, disbursement_date, remarks, dbt_transaction_id, disbursed_amount) VALUES
(1, 'SRT-2026-98124', 2, 1, 'disbursed', '2026-06-01 10:30:00', '2026-06-03 14:00:00', '2026-06-05 11:20:00', '2026-06-07 16:45:00', '2026-06-10 09:15:00', 'All land holding verification records cleared. First installment dispatched.', 'DBT-RBI-90182746352', 2000.00),
(2, 'SRT-2026-45109', 3, 4, 'approved', '2026-06-15 11:45:00', '2026-06-18 09:30:00', '2026-06-22 15:10:00', '2026-07-01 12:00:00', NULL, 'MUDRA project proposal approved by Nodal Credit Committee.', 'DBT-PENDING-STAGE', 0.00),
(3, 'SRT-2026-78210', 3, 5, 'field_verification', '2026-07-05 14:20:00', '2026-07-08 10:15:00', NULL, NULL, NULL, 'Academic records verified. District Education Officer site visit scheduled.', NULL, 0.00),
(4, 'SRT-2026-12904', 4, 3, 'under_scrutiny', '2026-07-20 09:10:00', NULL, NULL, NULL, NULL, 'Document scrutiny in progress by Health Department Officer.', NULL, 0.00),
(5, 'SRT-2026-66389', 2, 2, 'submitted', '2026-07-25 16:50:00', NULL, NULL, NULL, NULL, 'Application received. Pending initial officer assignment.', NULL, 0.00),
(6, 'SRT-2026-31207', 2, 8, 'approved', '2026-06-10 09:00:00', '2026-06-12 10:00:00', '2026-06-15 13:30:00', '2026-06-20 11:00:00', NULL, 'Crop insurance policy approved for current Kharif season.', 'DBT-PENDING-STAGE', 0.00),
(7, 'SRT-2026-52318', 3, 10, 'disbursed', '2026-05-02 09:30:00', '2026-05-05 11:00:00', '2026-05-10 14:20:00', '2026-05-18 10:00:00', '2026-05-25 09:45:00', 'PMAY-G house construction assistance released in full.', 'DBT-RBI-77281937465', 130000.00),
(8, 'SRT-2026-64029', 4, 12, 'submitted', '2026-07-28 12:15:00', NULL, NULL, NULL, NULL, 'JSY application received, awaiting ASHA worker verification.', NULL, 0.00),
(9, 'SRT-2026-70933', 2, 13, 'approved', '2026-04-01 08:00:00', '2026-04-02 09:00:00', '2026-04-03 10:00:00', '2026-04-04 11:00:00', NULL, 'PMSBY accident cover activated for the policy year.', 'DBT-PENDING-STAGE', 0.00),
(10, 'SRT-2026-81456', 3, 14, 'field_verification', '2026-07-01 10:00:00', '2026-07-04 09:30:00', NULL, NULL, NULL, 'PM-YASASVI eligibility documents under caste category verification.', NULL, 0.00),
(11, 'SRT-2026-90218', 4, 16, 'disbursed', '2026-03-10 09:00:00', '2026-03-12 10:00:00', '2026-03-15 11:00:00', '2026-03-20 12:00:00', '2026-03-28 10:30:00', 'PMMVY first installment credited after MCP registration.', 'DBT-RBI-65423190872', 1000.00),
(12, 'SRT-2026-11732', 2, 18, 'under_scrutiny', '2026-07-15 09:00:00', NULL, NULL, NULL, NULL, 'Atal Pension Yojana enrolment under bank verification.', NULL, 0.00),
(13, 'SRT-2026-20984', 3, 20, 'rejected', '2026-05-20 09:00:00', '2026-05-22 10:00:00', '2026-05-25 11:00:00', NULL, NULL, 'Project report did not meet minimum viability criteria for the loan slab.', NULL, 0.00);
 
-- 4. Documents
INSERT INTO documents (user_id, application_id, doc_type, file_name, file_path, verification_status) VALUES
(2, 1, 'Aadhaar Card', 'aadhaar_ramesh.pdf', 'uploads/aadhaar_ramesh.pdf', 'verified'),
(2, 1, 'Land Holding Record', 'khasra_khatouni.pdf', 'uploads/khasra_khatouni.pdf', 'verified'),
(3, 2, 'PAN & Aadhaar Card', 'priya_kyc_docs.pdf', 'uploads/priya_kyc_docs.pdf', 'verified'),
(3, 2, 'Business Plan Project', 'craft_boutique_plan.pdf', 'uploads/craft_boutique_plan.pdf', 'verified'),
(4, 4, 'Income Certificate', 'sunita_income_cert.pdf', 'uploads/sunita_income_cert.pdf', 'pending'),
(2, 6, 'Sowing Certificate', 'ramesh_sowing_cert.pdf', 'uploads/ramesh_sowing_cert.pdf', 'verified'),
(3, 7, 'SECC 2011 Proof', 'priya_secc_proof.pdf', 'uploads/priya_secc_proof.pdf', 'verified'),
(4, 11, 'MCP Card', 'sunita_mcp_card.pdf', 'uploads/sunita_mcp_card.pdf', 'verified');
 
-- 5. Notifications
INSERT INTO notifications (user_id, title, message, type, is_read) VALUES
(2, 'DBT Payment Disbursed', 'Rs. 2,000 has been credited to your HDFC Bank account under PM-KISAN. Ref: DBT-RBI-90182746352', 'success', FALSE),
(3, 'MUDRA Loan Approved', 'Your application SRT-2026-45109 for PM-MUDRA Yojana has been approved by the Nodal Officer.', 'success', FALSE),
(3, 'Field Verification Alert', 'Inspector assigned for your National Scholarship application SRT-2026-78210.', 'info', TRUE),
(4, 'Application Submitted', 'Your Ayushman Bharat application SRT-2026-12904 was received successfully.', 'info', FALSE),
(2, 'Crop Insurance Approved', 'Your PMFBY application SRT-2026-31207 has been approved for the current Kharif season.', 'success', FALSE),
(3, 'PMAY-G Assistance Disbursed', 'Rs. 1,30,000 has been credited to your account under PMAY-G. Ref: DBT-RBI-77281937465', 'success', TRUE),
(4, 'PMMVY Installment Credited', 'Rs. 1,000 has been credited under Pradhan Mantri Matru Vandana Yojana. Ref: DBT-RBI-65423190872', 'success', FALSE),
(3, 'Stand-Up India Application Rejected', 'Your application SRT-2026-20984 was rejected. Reason: project report did not meet minimum viability criteria.', 'danger', FALSE);
 
-- 6. Reminders
INSERT INTO reminders (user_id, title, due_date, reminder_type, description) VALUES
(2, 'Next PM-KISAN Installment', '2026-10-01', 'disbursement', 'Expected 2nd installment of Rs. 2,000 for FY 2026-27.'),
(3, 'Submit Income Renewal Cert', '2026-08-30', 'document_renewal', 'Upload updated annual income certificate for Scholarship continuation.'),
(2, 'PMSBY Annual Renewal', '2026-05-31', 'renewal', 'Renew Pradhan Mantri Suraksha Bima Yojana cover before the annual renewal date.'),
(2, 'Atal Pension Yojana Contribution Due', '2026-09-05', 'contribution', 'Monthly APY contribution auto-debit scheduled from linked bank account.');
 
-- 7. Grievances
INSERT INTO grievances (ticket_no, user_id, application_id, subject, description, status, response) VALUES
('GRV-2026-1092', 2, 1, 'Delay in e-KYC status update', 'My land record update was showing pending for 3 days.', 'resolved', 'e-KYC verified manually by District Revenue Inspector on June 4th.');
 
