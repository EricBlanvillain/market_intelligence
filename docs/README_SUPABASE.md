# Supabase Setup for Market Intelligence

## Overview

This document provides a summary of the Supabase setup process for the Market Intelligence application. We've created several scripts and guides to help you set up the necessary tables in your Supabase instance.

## Files

1. `create_tables.sql` - SQL script with commands to create all necessary tables
2. `setup_supabase.py` - Python script to check if tables exist and populate them with sample data
3. `create_tables_direct.py` - Python script to create tables directly using the Supabase client
4. `SUPABASE_SETUP_GUIDE.md` - Comprehensive guide for manually setting up tables in the Supabase dashboard

## Current Status

We've identified that the Market Intelligence application requires the following tables in Supabase:

- `market_data` - Stores Market data with custom keywords
- `reports` - Stores reports with custom keywords
- `queries` - Stores queries with custom keywords
- `workflows` - Stores workflows

Currently, only the `market_data` table exists in your Supabase instance, but it might not have all the required columns, particularly the `custom_keyword` column which is essential for filtering data in the Data Explorer.

## Recommended Setup Process

1. **Manual Table Creation (Recommended)**
   - Follow the instructions in `SUPABASE_SETUP_GUIDE.md` to manually create the tables in the Supabase dashboard
   - This is the most reliable method as it gives you direct control over the table schema

2. **SQL Script**
   - If you have access to the Supabase SQL Editor, you can run the commands in `create_tables.sql`
   - This will create all tables with the correct schema in one go

3. **Automated Setup**
   - Run `setup_supabase.py` to check if tables exist and populate them with sample data
   - If tables don't exist, follow the instructions to create them manually

## Troubleshooting

If you encounter issues with the Data Explorer not showing data from Supabase:

1. Check if all required tables exist in your Supabase instance
2. Verify that the tables have the correct schema, especially the `custom_keyword` column
3. Make sure your `.env` file contains the correct Supabase URL and API key
4. Check the console output for any error messages related to Supabase

## Next Steps

After setting up the tables:

1. Run `python setup_supabase.py` to populate the tables with sample data
2. Run `streamlit run multi_agent_app.py` to start the application
3. Test the Data Explorer to ensure it can retrieve data from Supabase

## Support

If you continue to experience issues, please provide the following information:

1. Error messages from the console
2. Screenshots of your Supabase table schemas
3. The output of `python setup_supabase.py`

This will help us diagnose and resolve any remaining issues with your Supabase setup.
