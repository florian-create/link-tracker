#!/usr/bin/env python3
"""
Migration script: Add ICP column to existing links table
Safe migration - does not delete any data
"""

import os
import psycopg2
from datetime import datetime

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/link_tracker')

print(f"🔧 Migration: Add ICP column to links table")
print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

def migrate():
    """Add ICP column to links table if it doesn't exist"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("\n📋 Checking if ICP column exists...")

        # Check if column exists
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'links' AND column_name = 'icp'
        """)

        if cur.fetchone():
            print("✅ ICP column already exists - no migration needed")
            cur.close()
            conn.close()
            return True

        print("🔄 Adding ICP column to links table...")

        # Count rows before
        cur.execute("SELECT COUNT(*) FROM links")
        count_before = cur.fetchone()[0]
        print(f"   Rows before migration: {count_before}")

        # Add ICP column
        cur.execute("""
            ALTER TABLE links
            ADD COLUMN icp VARCHAR(255)
        """)

        # Verify after
        cur.execute("SELECT COUNT(*) FROM links")
        count_after = cur.fetchone()[0]

        if count_before == count_after:
            print(f"✅ Migration successful - all {count_after} rows preserved")
        else:
            raise Exception(f"❌ Data loss detected! Before: {count_before}, After: {count_after}")

        conn.commit()
        cur.close()
        conn.close()

        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("\n⚠️  This script will add the 'icp' column to the links table")
    print("   Existing data will NOT be affected")
    print("   The column will allow NULL values by default")

    response = input("\nContinue? (yes/no): ").lower().strip()

    if response in ['yes', 'y', 'oui', 'o']:
        success = migrate()
        if success:
            print("\n🎉 You can now use the ICP field in your Clay configuration!")
            print("\nExample Clay body:")
            print('''
{
  "first_name": "{{first_name}}",
  "last_name": "{{last_name}}",
  "email": "{{email}}",
  "ICP": "{{ICP}}",
  "campaign": "wesser-recrutement.fr",
  "destination_url": "https://wesser-recrutement.fr/rejoindre"
}
            ''')
        else:
            print("\n⚠️  Migration failed. Please check the error above.")
    else:
        print("\n❌ Migration cancelled")
