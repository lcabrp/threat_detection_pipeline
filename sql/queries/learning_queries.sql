-- Data Engineering Learning: SQL Queries for Cybersecurity Analytics
-- This file demonstrates key SQL concepts for data engineering

-- ==============================================================================
-- BASIC AGGREGATION QUERIES (Foundation Level)
-- ==============================================================================

-- 1. Daily event summary with basic aggregations
SELECT 
    DATE(timestamp) as event_date,
    COUNT(*) as total_events,
    COUNT(DISTINCT user_name) as unique_users,
    COUNT(DISTINCT source_ip) as unique_ips,
    AVG(risk_score) as avg_risk_score,
    MAX(risk_score) as max_risk_score
FROM silver_security_events 
WHERE timestamp >= DATE('now', '-30 days')
GROUP BY DATE(timestamp)
ORDER BY event_date DESC;

-- 2. Event type distribution with percentages
SELECT 
    event_type,
    COUNT(*) as event_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM silver_security_events 
WHERE event_date >= DATE('now', '-7 days')
GROUP BY event_type
ORDER BY event_count DESC;

-- ==============================================================================
-- WINDOW FUNCTIONS (Intermediate Level)
-- ==============================================================================

-- 3. Ranking users by suspicious activity with window functions
SELECT 
    user_name,
    COUNT(*) as total_events,
    SUM(CASE WHEN is_suspicious THEN 1 ELSE 0 END) as suspicious_events,
    ROUND(AVG(risk_score), 2) as avg_risk_score,
    
    -- Window functions for ranking and comparison
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) as activity_rank,
    RANK() OVER (ORDER BY SUM(CASE WHEN is_suspicious THEN 1 ELSE 0 END) DESC) as suspicion_rank,
    
    -- Moving averages and trends
    AVG(COUNT(*)) OVER (
        ORDER BY user_name 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as moving_avg_events
    
FROM silver_security_events 
WHERE event_date >= DATE('now', '-30 days')
GROUP BY user_name
HAVING COUNT(*) >= 10  -- Filter for active users
ORDER BY suspicious_events DESC, total_events DESC;

-- 4. Time-based analysis with LAG/LEAD functions
SELECT 
    event_date,
    total_events,
    suspicious_events,
    
    -- Compare with previous day
    LAG(total_events, 1) OVER (ORDER BY event_date) as previous_day_events,
    total_events - LAG(total_events, 1) OVER (ORDER BY event_date) as daily_change,
    
    -- Compare with next day  
    LEAD(total_events, 1) OVER (ORDER BY event_date) as next_day_events,
    
    -- 7-day moving average
    AVG(total_events) OVER (
        ORDER BY event_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as seven_day_avg,
    
    -- Percentage change from previous day
    ROUND(
        (total_events - LAG(total_events, 1) OVER (ORDER BY event_date)) * 100.0 / 
        LAG(total_events, 1) OVER (ORDER BY event_date), 2
    ) as pct_change
    
FROM gold_daily_metrics 
WHERE metric_date >= DATE('now', '-60 days')
ORDER BY event_date;

-- ==============================================================================
-- ADVANCED ANALYTICS (Advanced Level)
-- ==============================================================================

-- 5. Cohort analysis: User behavior over time
WITH user_first_activity AS (
    SELECT 
        user_name,
        MIN(event_date) as first_activity_date,
        DATE('now') as analysis_date
    FROM silver_security_events
    GROUP BY user_name
),
user_monthly_activity AS (
    SELECT 
        se.user_name,
        ufa.first_activity_date,
        DATE(se.event_date, 'start of month') as activity_month,
        COUNT(*) as monthly_events,
        SUM(CASE WHEN se.is_suspicious THEN 1 ELSE 0 END) as monthly_suspicious
    FROM silver_security_events se
    JOIN user_first_activity ufa ON se.user_name = ufa.user_name
    GROUP BY se.user_name, ufa.first_activity_date, DATE(se.event_date, 'start of month')
)
SELECT 
    first_activity_date,
    COUNT(DISTINCT user_name) as cohort_size,
    activity_month,
    COUNT(DISTINCT user_name) as active_users,
    ROUND(COUNT(DISTINCT user_name) * 100.0 / 
          FIRST_VALUE(COUNT(DISTINCT user_name)) OVER (
              PARTITION BY first_activity_date 
              ORDER BY activity_month
          ), 2) as retention_rate
FROM user_monthly_activity
WHERE first_activity_date >= DATE('now', '-365 days')
GROUP BY first_activity_date, activity_month
ORDER BY first_activity_date, activity_month;

-- 6. Anomaly detection using statistical methods
WITH daily_stats AS (
    SELECT 
        event_date,
        total_events,
        AVG(total_events) OVER () as overall_avg,
        
        -- Calculate standard deviation manually (SQLite doesn't have STDDEV)
        AVG((total_events - AVG(total_events) OVER ()) * 
            (total_events - AVG(total_events) OVER ())) OVER () as variance,
        
        SQRT(AVG((total_events - AVG(total_events) OVER ()) * 
                 (total_events - AVG(total_events) OVER ())) OVER ()) as std_dev
    FROM gold_daily_metrics
    WHERE metric_date >= DATE('now', '-90 days')
),
anomaly_detection AS (
    SELECT 
        event_date,
        total_events,
        overall_avg,
        std_dev,
        ABS(total_events - overall_avg) / std_dev as z_score,
        
        -- Flag anomalies (z-score > 2 is typically considered anomalous)
        CASE 
            WHEN ABS(total_events - overall_avg) / std_dev > 2 THEN 'anomaly'
            WHEN ABS(total_events - overall_avg) / std_dev > 1.5 THEN 'unusual'
            ELSE 'normal'
        END as anomaly_flag
    FROM daily_stats
)
SELECT 
    event_date,
    total_events,
    ROUND(overall_avg, 0) as expected_events,
    ROUND(z_score, 2) as z_score,
    anomaly_flag,
    
    -- Calculate how unusual this day is
    ROUND((total_events - overall_avg) / overall_avg * 100, 1) as pct_deviation
FROM anomaly_detection
WHERE anomaly_flag != 'normal'
ORDER BY z_score DESC;

-- ==============================================================================
-- DATA QUALITY QUERIES
-- ==============================================================================

-- 7. Comprehensive data quality assessment
SELECT 
    'Completeness Check' as quality_dimension,
    'timestamp' as field_name,
    COUNT(*) as total_records,
    COUNT(timestamp) as non_null_records,
    COUNT(*) - COUNT(timestamp) as null_records,
    ROUND((COUNT(timestamp) * 100.0 / COUNT(*)), 2) as completeness_percentage
FROM silver_security_events
WHERE event_date >= DATE('now', '-7 days')

UNION ALL

SELECT 
    'Completeness Check',
    'user_name',
    COUNT(*),
    COUNT(user_name),
    COUNT(*) - COUNT(user_name),
    ROUND((COUNT(user_name) * 100.0 / COUNT(*)), 2)
FROM silver_security_events
WHERE event_date >= DATE('now', '-7 days')

UNION ALL

SELECT 
    'Validity Check',
    'risk_score',
    COUNT(*),
    COUNT(CASE WHEN risk_score BETWEEN 0 AND 100 THEN 1 END),
    COUNT(CASE WHEN risk_score NOT BETWEEN 0 AND 100 OR risk_score IS NULL THEN 1 END),
    ROUND((COUNT(CASE WHEN risk_score BETWEEN 0 AND 100 THEN 1 END) * 100.0 / COUNT(*)), 2)
FROM silver_security_events
WHERE event_date >= DATE('now', '-7 days')

UNION ALL

SELECT 
    'Consistency Check',
    'ip_format',
    COUNT(*),
    COUNT(CASE 
        WHEN source_ip LIKE '%.%.%.%' 
        AND LENGTH(source_ip) - LENGTH(REPLACE(source_ip, '.', '')) = 3 
        THEN 1 END),
    COUNT(CASE 
        WHEN source_ip NOT LIKE '%.%.%.%' 
        OR LENGTH(source_ip) - LENGTH(REPLACE(source_ip, '.', '')) != 3 
        THEN 1 END),
    ROUND((COUNT(CASE 
        WHEN source_ip LIKE '%.%.%.%' 
        AND LENGTH(source_ip) - LENGTH(REPLACE(source_ip, '.', '')) = 3 
        THEN 1 END) * 100.0 / COUNT(*)), 2)
FROM silver_security_events
WHERE event_date >= DATE('now', '-7 days');

-- ==============================================================================
-- PERFORMANCE OPTIMIZATION QUERIES
-- ==============================================================================

-- 8. Query performance analysis and optimization
-- Before optimization: Full table scan
EXPLAIN QUERY PLAN
SELECT user_name, COUNT(*) 
FROM silver_security_events 
WHERE event_date BETWEEN DATE('now', '-30 days') AND DATE('now')
GROUP BY user_name;

-- After optimization: Using indexes
EXPLAIN QUERY PLAN
SELECT user_name, COUNT(*) 
FROM silver_security_events 
WHERE event_date >= DATE('now', '-30 days')  -- Optimized date filter
  AND event_date <= DATE('now')
GROUP BY user_name;

-- 9. Partition-aware query (simulating partitioned data)
-- This demonstrates how to write queries that work efficiently with partitioned data
SELECT 
    SUBSTR(event_date, 1, 7) as year_month,  -- Partition key
    event_type,
    COUNT(*) as event_count,
    AVG(risk_score) as avg_risk_score
FROM silver_security_events 
WHERE event_date >= DATE('now', '-12 months')  -- Partition pruning
GROUP BY SUBSTR(event_date, 1, 7), event_type
ORDER BY year_month DESC, event_count DESC;

-- ==============================================================================
-- BUSINESS INTELLIGENCE QUERIES
-- ==============================================================================

-- 10. Executive dashboard query: Key security metrics
SELECT 
    'Last 24 Hours' as time_period,
    COUNT(*) as total_events,
    COUNT(CASE WHEN is_suspicious THEN 1 END) as suspicious_events,
    COUNT(CASE WHEN risk_category = 'critical' THEN 1 END) as critical_events,
    COUNT(DISTINCT user_name) as active_users,
    COUNT(DISTINCT source_ip) as unique_source_ips,
    ROUND(AVG(risk_score), 2) as avg_risk_score,
    MAX(risk_score) as max_risk_score
FROM silver_security_events 
WHERE timestamp >= DATETIME('now', '-24 hours')

UNION ALL

SELECT 
    'Last 7 Days',
    COUNT(*),
    COUNT(CASE WHEN is_suspicious THEN 1 END),
    COUNT(CASE WHEN risk_category = 'critical' THEN 1 END),
    COUNT(DISTINCT user_name),
    COUNT(DISTINCT source_ip),
    ROUND(AVG(risk_score), 2),
    MAX(risk_score)
FROM silver_security_events 
WHERE event_date >= DATE('now', '-7 days')

UNION ALL

SELECT 
    'Last 30 Days',
    COUNT(*),
    COUNT(CASE WHEN is_suspicious THEN 1 END),
    COUNT(CASE WHEN risk_category = 'critical' THEN 1 END),
    COUNT(DISTINCT user_name),
    COUNT(DISTINCT source_ip),
    ROUND(AVG(risk_score), 2),
    MAX(risk_score)
FROM silver_security_events 
WHERE event_date >= DATE('now', '-30 days');