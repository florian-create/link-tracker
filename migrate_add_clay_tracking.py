#!/usr/bin/env python3
"""
Migration script to add sent_to_clay and sent_to_clay_at columns to the links table.
Run this script once to update your existing database.

Usage: python migrate_add_clay_tracking.py
"""

import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/link_tracker')

def migrate():
    """Add Clay tracking columns to links table"""
    print("Starting migration...")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("Connected to database successfully")

        # Check if columns already exist
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='links' AND column_name IN ('sent_to_clay', 'sent_to_clay_at')
        """)

        existing_columns = [row[0] for row in cur.fetchall()]

        if len(existing_columns) == 2:
            print("✅ All columns already exist! No migration needed.")
            cur.close()
            conn.close()
            return

        print(f"Found {len(existing_columns)} existing columns: {existing_columns}")
        print("Adding missing columns...")

        # Add sent_to_clay if it doesn't exist
        if 'sent_to_clay' not in existing_columns:
            cur.execute("""
                ALTER TABLE links
                ADD COLUMN sent_to_clay BOOLEAN DEFAULT FALSE
            """)
            print("✅ Added column: sent_to_clay")

        # Add sent_to_clay_at if it doesn't exist
        if 'sent_to_clay_at' not in existing_columns:
            cur.execute("""
                ALTER TABLE links
                ADD COLUMN sent_to_clay_at TIMESTAMP
            """)
            print("✅ Added column: sent_to_clay_at")

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
