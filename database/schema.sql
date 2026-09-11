-- ============================================================
-- SAARTHI: Integrated Government Scheme & Citizen Benefit Tracker
-- Database DDL Schema (MySQL 8.0+)
-- ============================================================

CREATE DATABASE IF NOT EXISTS saarthi_db CHARACTER SET utf8 COLLATE utf8_general_ci;
USE saarthi_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aadhaar_no VARCHAR(12) UNIQUE NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    mobile VARCHAR(10) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('citizen', 'admin') DEFAULT 'citizen',
    dob DATE,
    gender ENUM('Male', 'Female', 'Transgender', 'Other'),
    category ENUM('General', 'OBC', 'SC', 'ST', 'EWS'),
    income_annual DECIMAL(12, 2) DEFAULT 0.00,
    occupation VARCHAR(100),
    state VARCHAR(80) DEFAULT 'Pan-India',
    district VARCHAR(80),
    address TEXT,
    dbt_bank_account VARCHAR(20),
    ifsc_code VARCHAR(11),
    bank_name VARCHAR(100),
    dbt_linked BOOLEAN DEFAULT TRUE,
    profile_completed INT DEFAULT 85,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 2. Government Schemes Table
CREATE TABLE IF NOT EXISTS schemes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    ministry VARCHAR(150) NOT NULL,
    category VARCHAR(80) NOT NULL,
    benefit_amount DECIMAL(12, 2) NOT NULL,
    benefit_type VARCHAR(100) DEFAULT 'Direct Benefit Transfer (DBT)',
    eligibility_min_age INT DEFAULT 0,
    eligibility_max_age INT DEFAULT 120,
    eligibility_max_income DECIMAL(12, 2) DEFAULT 1000000.00,
    gender_target VARCHAR(20) DEFAULT 'All',
    target_category VARCHAR(50) DEFAULT 'All',
    target_occupation VARCHAR(100) DEFAULT 'All',
    description TEXT NOT NULL,
    benefits_summary TEXT,
    documents_required TEXT,
    deadline DATE,
    status ENUM('active', 'inactive', 'upcoming') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 3. Scheme Applications Table
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_ref VARCHAR(40) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    scheme_id INT NOT NULL,
    status ENUM('submitted', 'under_scrutiny', 'field_verification', 'approved', 'disbursed', 'rejected') DEFAULT 'submitted',
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scrutiny_date TIMESTAMP NULL,
    verification_date TIMESTAMP NULL,
    approval_date TIMESTAMP NULL,
    disbursement_date TIMESTAMP NULL,
    remarks TEXT,
    rejection_reason TEXT,
    dbt_transaction_id VARCHAR(50),
    disbursed_amount DECIMAL(12, 2) DEFAULT 0.00,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 4. Digital Documents Vault Table
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    application_id INT NULL,
    doc_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_size INT DEFAULT 0,
    verification_status ENUM('pending', 'verified', 'rejected') DEFAULT 'verified',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 5. Citizen Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info', 'success', 'warning', 'danger') DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 6. Reminders Table
CREATE TABLE IF NOT EXISTS reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    due_date DATE NOT NULL,
    reminder_type VARCHAR(50) DEFAULT 'disbursement',
    description TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 7. Grievances & Support Tickets Table
CREATE TABLE IF NOT EXISTS grievances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_no VARCHAR(40) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    application_id INT NULL,
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('open', 'in_progress', 'resolved') DEFAULT 'open',
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Indexes for ultra-fast queries
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_schemes_category ON schemes(category);
CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);
