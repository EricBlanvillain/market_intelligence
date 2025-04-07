# Supabase Setup Guide for Market Intelligence

This guide will help you set up the necessary tables in your Supabase instance for the Market Intelligence application.

## Prerequisites

- Access to your Supabase dashboard
- Admin privileges to create tables and policies

## Step 1: Access the SQL Editor

1. Log in to your Supabase dashboard at https://app.supabase.io
2. Select your project
3. In the left sidebar, click on "SQL Editor"
4. Click "New Query" to create a new SQL query

## Step 2: Create the Tables

Copy and paste the following SQL commands into the SQL Editor and run them:

```sql
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
```

## Step 3: Create Indexes for Better Performance

Run the following SQL commands to create indexes:

```sql
-- Add indexes for better performance
CREATE INDEX idx_market_data_sector ON market_data(sector);
CREATE INDEX idx_market_data_country ON market_data(country);
CREATE INDEX idx_market_data_custom_keyword ON market_data(custom_keyword);

CREATE INDEX idx_reports_sector ON reports(sector);
CREATE INDEX idx_reports_country ON reports(country);
CREATE INDEX idx_reports_custom_keyword ON reports(custom_keyword);

CREATE INDEX idx_queries_custom_keyword ON queries(custom_keyword);
CREATE INDEX idx_queries_agent_type ON queries(agent_type);
```

## Step 4: Set Up Row-Level Security (RLS)

Run the following SQL commands to enable Row-Level Security and create policies:

```sql
-- Enable Row-Level Security
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
CREATE POLICY "Allow full access to authenticated users" ON market_data FOR ALL TO authenticated USING (true);
CREATE POLICY "Allow full access to authenticated users" ON reports FOR ALL TO authenticated USING (true);
CREATE POLICY "Allow full access to authenticated users" ON queries FOR ALL TO authenticated USING (true);
CREATE POLICY "Allow full access to authenticated users" ON workflows FOR ALL TO authenticated USING (true);

-- Create policies for anonymous access (for development purposes)
CREATE POLICY "Allow anon access" ON market_data FOR ALL TO anon USING (true);
CREATE POLICY "Allow anon access" ON reports FOR ALL TO anon USING (true);
CREATE POLICY "Allow anon access" ON queries FOR ALL TO anon USING (true);
CREATE POLICY "Allow anon access" ON workflows FOR ALL TO anon USING (true);
```

## Step 5: Verify Table Creation

1. In the left sidebar, click on "Table Editor"
2. You should see the following tables:
   - `market_data`
   - `reports`
   - `queries`
   - `workflows`
3. Click on each table to verify that they have the correct columns

## Step 6: Populate Tables with Sample Data

After creating the tables, run the `setup_supabase.py` script to populate them with sample data:

```bash
python setup_supabase.py
```

This script will:
1. Check if the tables exist
2. Add sample Market data
3. Add sample reports
4. Add sample queries

## Troubleshooting

### Table Creation Issues

If you encounter issues creating tables through the SQL Editor:

1. Make sure you have admin privileges for your Supabase project
2. Try creating the tables one by one
3. Check for any error messages in the SQL Editor

### Data Population Issues

If you encounter issues populating the tables with sample data:

1. Make sure your `.env` file contains the correct Supabase URL and API key
2. Check that the tables have the correct schema
3. Look for error messages in the console output

## Manual Table Creation

If you still have issues, you can create the tables manually through the Table Editor:

1. In the left sidebar, click on "Table Editor"
2. Click "Create a new table"
3. Enter the table name (e.g., `market_data`)
4. Add the columns with their respective data types:
   - `id` (UUID, Primary Key)
   - `sector` (Text)
   - `country` (Text)
   - `data_point` (Text)
   - `value` (Text)
   - `source` (Text)
   - `date` (Text)
   - `custom_keyword` (Text)
   - `metadata` (JSONB)
   - `created_at` (Timestamp with time zone, Default: NOW())
5. Click "Save" to create the table
6. Repeat for the other tables

## Next Steps

After setting up the tables, you can run the Market Intelligence application:

```bash
streamlit run multi_agent_app.py
```

The application should now be able to store and retrieve data from your Supabase instance.
