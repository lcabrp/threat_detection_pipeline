-- Data Engineering Learning: Database Schema Design
-- This file demonstrates DDL (Data Definition Language) for cybersecurity analytics

-- ==============================================================================
-- BRONZE LAYER TABLES (Raw Data Storage)
-- ==============================================================================

-- Raw security logs table
CREATE TABLE IF NOT EXISTS bronze_security_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id VARCHAR(50) UNIQUE NOT NULL,
    timestamp DATETIME NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    source_ip VARCHAR(15) NOT NULL,
    destination_ip VARCHAR(15),
    user_name VARCHAR(100),
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    bytes_transferred INTEGER,
    response_time_ms INTEGER,
    risk_score DECIMAL(5,2),
    raw_data TEXT,  -- Original JSON for debugging
    ingestion_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexing for performance (important DE concept)
    INDEX idx_timestamp (timestamp),
    INDEX idx_event_type (event_type),
    INDEX idx_source_ip (source_ip),
    INDEX idx_severity (severity)
);

-- ==============================================================================
-- SILVER LAYER TABLES (Cleaned and Validated Data)
-- ==============================================================================

-- Cleaned and enriched security events
CREATE TABLE IF NOT EXISTS silver_security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id VARCHAR(50) UNIQUE NOT NULL,
    event_date DATE NOT NULL,
    event_hour INTEGER CHECK (event_hour >= 0 AND event_hour <= 23),
    timestamp DATETIME NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_category VARCHAR(50), -- Grouped categories for analysis
    source_ip VARCHAR(15) NOT NULL,
    destination_ip VARCHAR(15),
    user_name VARCHAR(100),
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    risk_score DECIMAL(5,2),
    risk_category VARCHAR(20) CHECK (risk_category IN ('low', 'medium', 'high', 'critical')),
    is_suspicious BOOLEAN NOT NULL DEFAULT FALSE,
    bytes_transferred INTEGER,
    response_time_ms INTEGER,
    
    -- Data lineage and quality tracking
    source_file VARCHAR(255),
    processed_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_quality_score DECIMAL(3,2), -- 0.00 to 1.00
    pipeline_version VARCHAR(10),
    
    -- Performance indexes
    INDEX idx_event_date (event_date),
    INDEX idx_event_hour (event_hour),
    INDEX idx_event_category (event_category),
    INDEX idx_risk_category (risk_category),
    INDEX idx_is_suspicious (is_suspicious),
    INDEX idx_user_name (user_name)
);

-- User activity summary (slowly changing dimension)
CREATE TABLE IF NOT EXISTS silver_user_profiles (
    user_name VARCHAR(100) PRIMARY KEY,
    first_seen_date DATE NOT NULL,
    last_seen_date DATE NOT NULL,
    total_events INTEGER DEFAULT 0,
    suspicious_events INTEGER DEFAULT 0,
    avg_risk_score DECIMAL(5,2),
    max_risk_score DECIMAL(5,2),
    primary_source_ip VARCHAR(15),
    event_types TEXT, -- JSON array of event types
    risk_profile VARCHAR(20), -- low, medium, high, critical
    is_active BOOLEAN DEFAULT TRUE,
    
    -- SCD Type 2 fields (Slowly Changing Dimensions)
    valid_from DATETIME DEFAULT CURRENT_TIMESTAMP,
    valid_to DATETIME,
    is_current BOOLEAN DEFAULT TRUE,
    
    INDEX idx_risk_profile (risk_profile),
    INDEX idx_is_active (is_active),
    INDEX idx_last_seen (last_seen_date)
);

-- ==============================================================================
-- GOLD LAYER TABLES (Analytics and Reporting)
-- ==============================================================================

-- Daily security metrics (fact table)
CREATE TABLE IF NOT EXISTS gold_daily_metrics (
    metric_date DATE PRIMARY KEY,
    total_events INTEGER NOT NULL,
    suspicious_events INTEGER NOT NULL,
    critical_events INTEGER NOT NULL,
    unique_users INTEGER NOT NULL,
    unique_source_ips INTEGER NOT NULL,
    
    -- Event type breakdown
    login_events INTEGER DEFAULT 0,
    malware_events INTEGER DEFAULT 0,
    network_scan_events INTEGER DEFAULT 0,
    file_access_events INTEGER DEFAULT 0,
    
    -- Risk metrics
    avg_risk_score DECIMAL(5,2),
    max_risk_score DECIMAL(5,2),
    high_risk_events INTEGER DEFAULT 0,
    
    -- Performance metrics
    avg_response_time_ms DECIMAL(8,2),
    total_bytes_transferred BIGINT DEFAULT 0,
    
    -- Time-based patterns
    peak_hour INTEGER,
    peak_hour_events INTEGER,
    
    -- Data quality metrics
    data_quality_score DECIMAL(3,2),
    records_processed INTEGER,
    records_failed INTEGER,
    
    -- Metadata
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    pipeline_run_id VARCHAR(100),
    
    INDEX idx_suspicious_events (suspicious_events),
    INDEX idx_avg_risk_score (avg_risk_score)
);

-- Threat intelligence summary
CREATE TABLE IF NOT EXISTS gold_threat_intelligence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date DATE NOT NULL,
    threat_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    
    -- Threat details
    affected_systems INTEGER,
    attack_patterns TEXT, -- JSON
    indicators_of_compromise TEXT, -- JSON array
    
    -- Impact assessment
    risk_level VARCHAR(20),
    potential_impact VARCHAR(255),
    
    -- Response metrics
    detection_time_hours DECIMAL(6,2),
    response_time_hours DECIMAL(6,2),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'active', -- active, contained, resolved
    assigned_analyst VARCHAR(100),
    
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_report_date (report_date),
    INDEX idx_threat_type (threat_type),
    INDEX idx_severity (severity),
    INDEX idx_status (status)
);

-- ==============================================================================
-- DIMENSION TABLES (for dimensional modeling)
-- ==============================================================================

-- Time dimension (common in data warehousing)
CREATE TABLE IF NOT EXISTS dim_time (
    time_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    
    INDEX idx_full_date (full_date),
    INDEX idx_year_month (year, month),
    INDEX idx_is_weekend (is_weekend)
);

-- IP geolocation dimension (for network analysis)
CREATE TABLE IF NOT EXISTS dim_ip_geolocation (
    ip_address VARCHAR(15) PRIMARY KEY,
    country_code VARCHAR(2),
    country_name VARCHAR(100),
    region VARCHAR(100),
    city VARCHAR(100),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    is_internal BOOLEAN NOT NULL DEFAULT FALSE,
    network_segment VARCHAR(20),
    
    -- Threat intelligence flags
    is_known_threat BOOLEAN DEFAULT FALSE,
    threat_category VARCHAR(50),
    first_seen_date DATE,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_country_code (country_code),
    INDEX idx_is_internal (is_internal),
    INDEX idx_is_known_threat (is_known_threat)
);

-- ==============================================================================
-- AUDIT AND MONITORING TABLES
-- ==============================================================================

-- Pipeline execution tracking
CREATE TABLE IF NOT EXISTS audit_pipeline_runs (
    run_id VARCHAR(100) PRIMARY KEY,
    dag_id VARCHAR(100) NOT NULL,
    task_id VARCHAR(100) NOT NULL,
    execution_date DATE NOT NULL,
    start_timestamp DATETIME NOT NULL,
    end_timestamp DATETIME,
    status VARCHAR(20) CHECK (status IN ('running', 'success', 'failed', 'retry')),
    
    -- Metrics
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    processing_time_seconds INTEGER,
    
    -- Error tracking  
    error_message TEXT,
    error_count INTEGER DEFAULT 0,
    
    -- Resource usage
    memory_usage_mb DECIMAL(10,2),
    cpu_usage_percent DECIMAL(5,2),
    
    INDEX idx_dag_task (dag_id, task_id),
    INDEX idx_execution_date (execution_date),
    INDEX idx_status (status)
);

-- Data quality monitoring
CREATE TABLE IF NOT EXISTS audit_data_quality (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name VARCHAR(100) NOT NULL,
    check_date DATE NOT NULL,
    check_type VARCHAR(50) NOT NULL, -- completeness, accuracy, consistency, etc.
    
    -- Quality metrics
    total_records INTEGER NOT NULL,
    passed_records INTEGER NOT NULL,
    failed_records INTEGER NOT NULL,
    quality_score DECIMAL(5,2) NOT NULL, -- percentage
    
    -- Specific checks
    null_count INTEGER DEFAULT 0,
    duplicate_count INTEGER DEFAULT 0,
    format_error_count INTEGER DEFAULT 0,
    business_rule_failures INTEGER DEFAULT 0,
    
    -- Threshold monitoring
    quality_threshold DECIMAL(5,2) DEFAULT 95.00,
    meets_threshold BOOLEAN NOT NULL,
    
    -- Details
    check_details TEXT, -- JSON with specific failure details
    remediation_actions TEXT,
    
    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_table_check_date (table_name, check_date),
    INDEX idx_meets_threshold (meets_threshold),
    INDEX idx_quality_score (quality_score)
);