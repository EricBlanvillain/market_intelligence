-- SQL script to create tables for Market Intelligence platform
-- Run this in the Supabase SQL Editor

-- Drop existing tables if they exist
DROP TABLE IF EXISTS market_data;
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS queries;
DROP TABLE IF EXISTS workflows;

-- Create market_data table
CREATE TABLE market_data (
    id UUID PRIMARY KEY,
    sector TEXT,
    country TEXT,
    data_point TEXT,
    value TEXT,
    source TEXT,
    date TEXT,
    custom_keyword TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY,
    title TEXT,
    sector TEXT,
    country TEXT,
    financial_product TEXT,
    content TEXT,
    summary TEXT,
    custom_keyword TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Create queries table
CREATE TABLE queries (
    id UUID PRIMARY KEY,
    query_text TEXT,
    query TEXT,
    entities JSONB,
    intent TEXT,
    response TEXT,
    result TEXT,
    agent_type TEXT,
    custom_keyword TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Create workflows table
CREATE TABLE workflows (
    id UUID PRIMARY KEY,
    name TEXT,
    description TEXT,
    steps JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT,
    metadata JSONB
);

-- Add indexes for better performance
CREATE INDEX idx_market_data_sector ON market_data(sector);
CREATE INDEX idx_market_data_country ON market_data(country);
CREATE INDEX idx_market_data_custom_keyword ON market_data(custom_keyword);

CREATE INDEX idx_reports_sector ON reports(sector);
CREATE INDEX idx_reports_country ON reports(country);
CREATE INDEX idx_reports_custom_keyword ON reports(custom_keyword);

CREATE INDEX idx_queries_custom_keyword ON queries(custom_keyword);
CREATE INDEX idx_queries_agent_type ON queries(agent_type);

-- Grant access to authenticated users
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Allow full access to authenticated users" ON market_data FOR ALL TO authenticated USING (true);
CREATE POLICY "Allow full access to authenticated users" ON reports FOR ALL TO authenticated USING (true);
CREATE POLICY "Allow full access to authenticated users" ON queries FOR ALL TO authenticated USING (true);
CREATE POLICY "Allow full access to authenticated users" ON workflows FOR ALL TO authenticated USING (true);

-- Also allow anon access for development purposes
CREATE POLICY "Allow anon access" ON market_data FOR ALL TO anon USING (true);
CREATE POLICY "Allow anon access" ON reports FOR ALL TO anon USING (true);
CREATE POLICY "Allow anon access" ON queries FOR ALL TO anon USING (true);
CREATE POLICY "Allow anon access" ON workflows FOR ALL TO anon USING (true);
