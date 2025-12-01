#!/usr/bin/env python3
"""
Migration script to add company_name, company_url, and linkedin_url columns to the links table.
Run this script once to update your existing database.

Usage: python migrate_add_company_fields.py
"""

import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/link_tracker')

def migrate():
    """Add new columns to links table"""
    print("Starting migration...")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("Connected to database successfully")

        # Check if columns already exist
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='links' AND column_name IN ('company_name', 'company_url', 'linkedin_url')
        """)

        existing_columns = [row[0] for row in cur.fetchall()]

        if len(existing_columns) == 3:
            print("✅ All columns already exist! No migration needed.")
            cur.close()
            conn.close()
            return

        print(f"Found {len(existing_columns)} existing columns: {existing_columns}")
        print("Adding missing columns...")

        # Add company_name if it doesn't exist
        if 'company_name' not in existing_columns:
            cur.execute("""
                ALTER TABLE links
                ADD COLUMN company_name VARCHAR(255)
            """)
            print("✅ Added column: company_name")

        # Add company_url if it doesn't exist
        if 'company_url' not in existing_columns:
            cur.execute("""
                ALTER TABLE links
                ADD COLUMN company_url TEXT
            """)
            print("✅ Added column: company_url")

        # Add linkedin_url if it doesn't exist
        if 'linkedin_url' not in existing_columns:
            cur.execute("""
                ALTER TABLE links
                ADD COLUMN linkedin_url TEXT
            """)
            print("✅ Added column: linkedin_url")

        conn.commit()

        # Verify the migration
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name='links'
            ORDER BY ordinal_position
        """)

        print("\n📋 Current table structure:")
        for row in cur.fetchall():
            print(f"  - {row[0]}: {row[1]}")

        cur.close()
        conn.close()

        print("\n✅ Migration completed successfully!")

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise

if __name__ == '__main__':
    migrate()
