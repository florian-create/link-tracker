#!/usr/bin/env python3
"""Script to initialize the database tables"""

import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    exit(1)

print(f"Connecting to database...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    print("Creating 'links' table...")
    cur.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id SERIAL PRIMARY KEY,
            link_id VARCHAR(10) UNIQUE NOT NULL,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            email VARCHAR(255),
            campaign VARCHAR(255),
            destination_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    print("Creating 'clicks' table...")
    cur.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id SERIAL PRIMARY KEY,
            link_id VARCHAR(10) NOT NULL,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            user_agent TEXT,
            country VARCHAR(100),
            city VARCHAR(100),
            referer TEXT,
            FOREIGN KEY (link_id) REFERENCES links(link_id)
        )
    ''')

    conn.commit()
    print("✅ Database tables created successfully!")

    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
