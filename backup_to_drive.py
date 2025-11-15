#!/usr/bin/env python3
"""
Automated backup script for Link Tracker database to Google Drive
Exports both links and clicks tables as CSV files and uploads them to Google Drive

Usage:
    python backup_to_drive.py

Environment Variables Required:
    DATABASE_URL - PostgreSQL connection string
    GOOGLE_SERVICE_ACCOUNT_JSON - Path to Google service account JSON file
    GOOGLE_DRIVE_FOLDER_ID - Google Drive folder ID for backups (optional)
"""

import os
import csv
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import sys

# Configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/link_tracker')
SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', 'service-account.json')
DRIVE_FOLDER_ID = os.environ.get('GOOGLE_DRIVE_FOLDER_ID', None)  # Optional: specific folder

# Google Drive API Scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(DATABASE_URL)


def export_table_to_csv(table_name, query, filename):
    """Export a table to CSV file"""
    print(f"📊 Exporting {table_name} table...")

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute(query)
        rows = cur.fetchall()

        if not rows:
            print(f"⚠️  No data found in {table_name} table")
            return None

        # Write to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if len(rows) > 0:
                fieldnames = rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for row in rows:
                    writer.writerow(row)

        print(f"✅ Exported {len(rows)} rows to {filename}")
        return filename

    except Exception as e:
        print(f"❌ Error exporting {table_name}: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def upload_to_google_drive(filename, mime_type='text/csv'):
    """Upload file to Google Drive"""
    try:
        print(f"🔐 Authenticating with Google Drive...")

        # Check if service account file exists
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"❌ Service account file not found: {SERVICE_ACCOUNT_FILE}")
            print(f"💡 Please create a Google service account and download the JSON file")
            return False

        # Authenticate
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        service = build('drive', 'v3', credentials=credentials)

        # Prepare file metadata
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        drive_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.csv"

        file_metadata = {
            'name': drive_filename,
        }

        # Add folder if specified
        if DRIVE_FOLDER_ID:
            file_metadata['parents'] = [DRIVE_FOLDER_ID]

        # Upload file
        print(f"☁️  Uploading {drive_filename} to Google Drive...")
        media = MediaFileUpload(filename, mimetype=mime_type, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()

        print(f"✅ Upload successful!")
        print(f"   File ID: {file.get('id')}")
        print(f"   File name: {file.get('name')}")
        if file.get('webViewLink'):
            print(f"   Link: {file.get('webViewLink')}")

        return True

    except Exception as e:
        print(f"❌ Error uploading to Google Drive: {e}")
        print(f"💡 Make sure:")
        print(f"   1. Service account JSON file exists at: {SERVICE_ACCOUNT_FILE}")
        print(f"   2. Google Drive API is enabled in your Google Cloud project")
        print(f"   3. Service account has access to the Drive folder")
        return False


def cleanup_local_file(filename):
    """Remove local CSV file after upload"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"🗑️  Cleaned up local file: {filename}")
    except Exception as e:
        print(f"⚠️  Could not remove local file {filename}: {e}")


def backup_database():
    """Main backup function"""
    print("=" * 60)
    print("🚀 Link Tracker Database Backup Started")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Define tables to export
    tables = [
        {
            'name': 'links',
            'query': '''
                SELECT
                    id, link_id, first_name, last_name, email,
                    icp, campaign, destination_url, created_at
                FROM links
                ORDER BY created_at DESC
            ''',
            'filename': 'links_backup.csv'
        },
        {
            'name': 'clicks',
            'query': '''
                SELECT
                    c.id, c.link_id, c.clicked_at, c.ip_address,
                    c.user_agent, c.country, c.city, c.referer,
                    l.first_name, l.last_name, l.email, l.campaign, l.icp
                FROM clicks c
                JOIN links l ON c.link_id = l.link_id
                ORDER BY c.clicked_at DESC
            ''',
            'filename': 'clicks_backup.csv'
        }
    ]

    backup_successful = True

    # Export and upload each table
    for table in tables:
        filename = export_table_to_csv(
            table['name'],
            table['query'],
            table['filename']
        )

        if filename:
            # Upload to Google Drive
            success = upload_to_google_drive(filename)

            if success:
                # Clean up local file
                cleanup_local_file(filename)
            else:
                backup_successful = False
                print(f"⚠️  Keeping local backup: {filename}")
        else:
            backup_successful = False

    print("=" * 60)
    if backup_successful:
        print("✅ Backup completed successfully!")
    else:
        print("⚠️  Backup completed with warnings/errors")
    print("=" * 60)

    return backup_successful


if __name__ == '__main__':
    try:
        success = backup_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
