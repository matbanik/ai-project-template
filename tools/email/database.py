"""
SQLite database module for email storage.
Optimized for analytics queries on sender, subject, body, and timestamp.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR / 'emails.db'


def get_connection() -> sqlite3.Connection:
    """Get a database connection with optimized settings."""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrent read performance
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_database():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            sender TEXT NOT NULL,
            subject TEXT,
            body TEXT,
            timestamp DATETIME NOT NULL,
            fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            platform TEXT DEFAULT 'unknown',
            notification_type TEXT DEFAULT 'general',
            original_url TEXT,
            account TEXT DEFAULT 'matbanik'
        )
    ''')

    # Indexes for common analytics queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_emails_timestamp ON emails(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_emails_sender ON emails(sender)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_emails_platform ON emails(platform)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_emails_notification_type ON emails(notification_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_emails_account ON emails(account)')

    # Track sync state for incremental fetching
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized: {DB_FILE}")


def upsert_email(
    email_id: str,
    sender: str,
    subject: str,
    body: str,
    timestamp: datetime,
    platform: str = 'unknown',
    notification_type: str = 'general',
    original_url: Optional[str] = None
):
    """
    Insert or update an email record.

    Args:
        email_id: Gmail message ID (unique)
        sender: From address
        subject: Email subject
        body: Email body (plain text)
        timestamp: Email date/time
        platform: Detected social platform
        notification_type: Type of notification (comment, reply, etc.)
        original_url: URL of the original post
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO emails (id, sender, subject, body, timestamp, fetched_at, platform, notification_type, original_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            sender = excluded.sender,
            subject = excluded.subject,
            body = excluded.body,
            timestamp = excluded.timestamp,
            fetched_at = excluded.fetched_at,
            platform = excluded.platform,
            notification_type = excluded.notification_type,
            original_url = excluded.original_url
    ''', (email_id, sender, subject, body, timestamp, datetime.now(), platform, notification_type, original_url))

    conn.commit()
    conn.close()


def upsert_emails_batch(emails: list[dict]):
    """
    Batch insert or update email records for efficiency.

    Args:
        emails: List of dicts with keys: id, sender, subject, body, timestamp
    """
    if not emails:
        return

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now()
    data = [
        (
            e['id'],
            e['sender'],
            e['subject'],
            e['body'],
            e['timestamp'],
            now,
            e.get('platform', 'unknown'),
            e.get('notification_type', 'general'),
            e.get('original_url'),
            e.get('account', 'matbanik')
        )
        for e in emails
    ]

    cursor.executemany('''
        INSERT INTO emails (id, sender, subject, body, timestamp, fetched_at, platform, notification_type, original_url, account)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            sender = excluded.sender,
            subject = excluded.subject,
            body = excluded.body,
            timestamp = excluded.timestamp,
            fetched_at = excluded.fetched_at,
            platform = excluded.platform,
            notification_type = excluded.notification_type,
            original_url = excluded.original_url,
            account = excluded.account
    ''', data)

    conn.commit()
    conn.close()


def get_last_sync_timestamp() -> Optional[datetime]:
    """Get the timestamp of the last successful sync."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM sync_state WHERE key = 'last_sync'")
    row = cursor.fetchone()
    conn.close()

    if row:
        return datetime.fromisoformat(row['value'])
    return None


def set_last_sync_timestamp(timestamp: datetime):
    """Record the timestamp of the last successful sync."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO sync_state (key, value) VALUES ('last_sync', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    ''', (timestamp.isoformat(),))

    conn.commit()
    conn.close()


def email_exists(email_id: str) -> bool:
    """Check if an email already exists in the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM emails WHERE id = ?", (email_id,))
    exists = cursor.fetchone() is not None
    conn.close()

    return exists


def get_email_count() -> int:
    """Get the total number of emails in the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM emails")
    count = cursor.fetchone()['count']
    conn.close()

    return count


def get_existing_ids() -> set[str]:
    """Get all existing email IDs for deduplication."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM emails")
    ids = {row['id'] for row in cursor.fetchall()}
    conn.close()

    return ids


if __name__ == '__main__':
    # Initialize database
    init_database()
    print(f"Email count: {get_email_count()}")
