#!/usr/bin/env python3
"""
Email SQLite Database Module
============================
Stores fetched emails and drafted responses.

Database: tools/email/email_data.db

Tables:
- emails: Fetched emails from Gmail accounts
- responses: Drafted responses (for manual copy/paste to platform)
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = Path(__file__).parent / "email_data.db"


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Emails table - stores fetched emails
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY,
            gmail_id TEXT UNIQUE NOT NULL,
            thread_id TEXT,
            account TEXT NOT NULL,
            from_email TEXT NOT NULL,
            from_name TEXT,
            to_email TEXT,
            subject TEXT,
            snippet TEXT,
            body_text TEXT,
            body_html TEXT,
            date TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            labels TEXT,
            has_attachments BOOLEAN DEFAULT FALSE,
            responded BOOLEAN DEFAULT FALSE,
            response_id INTEGER,
            platform TEXT,
            FOREIGN KEY (response_id) REFERENCES responses(id)
        )
    """)
    
    # Responses table - drafted responses for manual use
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id INTEGER NOT NULL,
            account TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            used_at TEXT,
            notes TEXT,
            FOREIGN KEY (email_id) REFERENCES emails(id)
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_gmail_id ON emails(gmail_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_account ON emails(account)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_responded ON emails(responded)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_from ON emails(from_email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_responses_email ON responses(email_id)")
    
    conn.commit()
    conn.close()
    print(f"✓ Email database initialized: {DB_PATH}")


def email_exists(gmail_id: str) -> bool:
    """Check if an email with this Gmail ID already exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM emails WHERE gmail_id = ?", (gmail_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def save_email(email: Dict[str, Any]) -> bool:
    """
    Save an email to the database. Returns True if new, False if duplicate.
    
    Expected email dict:
        - gmail_id: Gmail message ID
        - thread_id: Gmail thread ID
        - account: Account name (matbanik, banikm)
        - from_email: Sender email
        - from_name: Sender name
        - to_email: Recipient
        - subject: Subject line
        - snippet: Gmail snippet
        - body_text: Plain text body
        - body_html: HTML body (optional)
        - date: Email date
        - labels: Comma-separated labels
        - has_attachments: Boolean
    """
    if email_exists(email['gmail_id']):
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO emails (
            gmail_id, thread_id, account, from_email, from_name, to_email,
            subject, snippet, body_text, body_html, date, fetched_at,
            labels, has_attachments
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        email['gmail_id'],
        email.get('thread_id'),
        email['account'],
        email['from_email'],
        email.get('from_name'),
        email.get('to_email'),
        email.get('subject'),
        email.get('snippet'),
        email.get('body_text'),
        email.get('body_html'),
        email['date'],
        datetime.utcnow().isoformat(),
        email.get('labels'),
        email.get('has_attachments', False)
    ))
    
    conn.commit()
    conn.close()
    return True


def save_emails_batch(emails: List[Dict[str, Any]]) -> Dict[str, int]:
    """Save multiple emails, skipping duplicates."""
    new_count = 0
    dup_count = 0
    
    for email in emails:
        if save_email(email):
            new_count += 1
        else:
            dup_count += 1
    
    return {'new': new_count, 'duplicate': dup_count}


def get_unresponded_emails(account: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """Get emails that haven't been responded to yet."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if account:
        cursor.execute("""
            SELECT * FROM emails 
            WHERE responded = FALSE AND account = ?
            ORDER BY date DESC
            LIMIT ?
        """, (account, limit))
    else:
        cursor.execute("""
            SELECT * FROM emails 
            WHERE responded = FALSE
            ORDER BY date DESC
            LIMIT ?
        """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_email_by_id(db_id: int) -> Optional[Dict]:
    """Get an email by its database ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emails WHERE id = ?", (db_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_response(email_id: int, account: str, content: str, notes: str = None) -> int:
    """Create a response draft. Returns the response ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO responses (email_id, account, content, created_at, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (email_id, account, content, datetime.utcnow().isoformat(), notes))
    
    response_id = cursor.lastrowid
    
    # Mark email as responded
    cursor.execute("UPDATE emails SET responded = TRUE, response_id = ? WHERE id = ?",
                   (response_id, email_id))
    
    conn.commit()
    conn.close()
    return response_id


def get_response_by_id(response_id: int) -> Optional[Dict]:
    """Get a response with associated email info."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT r.*, e.from_email, e.from_name, e.subject, e.snippet, e.body_text
        FROM responses r
        JOIN emails e ON r.email_id = e.id
        WHERE r.id = ?
    """, (response_id,))
    
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_responses(unused_only: bool = False, limit: int = 50) -> List[Dict]:
    """Get all responses, optionally filtering to unused only."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if unused_only:
        cursor.execute("""
            SELECT r.*, e.from_email, e.subject
            FROM responses r
            JOIN emails e ON r.email_id = e.id
            WHERE r.used = FALSE
            ORDER BY r.created_at DESC
            LIMIT ?
        """, (limit,))
    else:
        cursor.execute("""
            SELECT r.*, e.from_email, e.subject
            FROM responses r
            JOIN emails e ON r.email_id = e.id
            ORDER BY r.created_at DESC
            LIMIT ?
        """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_response_used(response_id: int) -> bool:
    """Mark a response as used (copied to platform)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE responses SET used = TRUE, used_at = ? WHERE id = ?
    """, (datetime.utcnow().isoformat(), response_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def update_response(response_id: int, content: str) -> bool:
    """Update a response's content."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE responses SET content = ? WHERE id = ?", (content, response_id))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def get_stats() -> Dict[str, Any]:
    """Get database statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    cursor.execute("SELECT COUNT(*) FROM emails")
    stats['total_emails'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM emails WHERE responded = TRUE")
    stats['responded_emails'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM responses")
    stats['total_responses'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM responses WHERE used = FALSE")
    stats['unused_responses'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT account, COUNT(*) as count FROM emails GROUP BY account")
    stats['emails_by_account'] = {row['account']: row['count'] for row in cursor.fetchall()}
    
    conn.close()
    return stats


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--stats':
        init_db()
        stats = get_stats()
        print("\n📊 Email Database Stats:")
        print(f"   Total emails: {stats['total_emails']}")
        print(f"   Responded: {stats['responded_emails']}")
        print(f"   Total responses: {stats['total_responses']}")
        print(f"   Unused responses: {stats['unused_responses']}")
        if stats['emails_by_account']:
            print("\n   Emails by account:")
            for acc, count in stats['emails_by_account'].items():
                print(f"     {acc}: {count}")
    else:
        init_db()
        print("\nUsage: python db.py --stats")
