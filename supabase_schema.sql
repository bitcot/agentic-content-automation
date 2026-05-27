-- Run this script in the Supabase SQL Editor to set up your tables

CREATE TABLE brand_context (
    id SERIAL PRIMARY KEY, 
    key VARCHAR UNIQUE, 
    value TEXT, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE content_logs (
    id SERIAL PRIMARY KEY, 
    topic VARCHAR, 
    icp_score FLOAT, 
    platform VARCHAR, 
    content TEXT, 
    status VARCHAR DEFAULT 'draft', 
    needs_human_check BOOLEAN DEFAULT TRUE, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    published_at TIMESTAMP
);

CREATE TABLE performance_metrics (
    id SERIAL PRIMARY KEY, 
    content_id INTEGER REFERENCES content_logs(id), 
    impressions INTEGER DEFAULT 0, 
    engagement_rate FLOAT DEFAULT 0.0, 
    clicks INTEGER DEFAULT 0, 
    conversions INTEGER DEFAULT 0, 
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
