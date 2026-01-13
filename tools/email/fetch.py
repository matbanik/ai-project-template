#!/usr/bin/env python3
"""
Email Fetcher with Database Storage
====================================
Fetches emails from Gmail accounts and stores them in SQLite.

Usage:
    python fetch.py                    # Fetch from all accounts
    python fetch.py --account matbanik # Fetch from specific account
    python fetch.py --limit 50         # Fetch more messages
    python fetch.py --query "is:unread"# Gmail search query
    python fetch.py --stats            # Show database stats
    python fetch.py --inbox            # Show unresponded emails

Requirements:
    pip install google-auth google-auth-oauthlib google-api-python-client
"""

import argparse
import base64
import email
import re
import sys
from typing import Dict, List, Optional

from auth import get_gmail_service, get_all_accounts
from db import init_db, save_emails_batch, get_unresponded_emails, get_stats, get_email_by_id


def parse_email_address(raw: str) -> tuple:
    """Parse 'Name <email@domain.com>' into (name, email)."""
    if not raw:
        return None, None
    
    match = re.match(r'^"?([^"<]*)"?\s*<?([^>]+)>?$', raw.strip())
    if match:
        name = match.group(1).strip() or None
        email_addr = match.group(2).strip()
        return name, email_addr
    return None, raw


def get_body_from_payload(payload: dict) -> tuple:
    """Extract plain text and HTML body from message payload."""
    text_body = None
    html_body = None
    
    def extract_parts(part):
        nonlocal text_body, html_body
        
        mime_type = part.get('mimeType', '')
        body = part.get('body', {})
        data = body.get('data', '')
        
        if mime_type == 'text/plain' and data and not text_body:
            text_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        elif mime_type == 'text/html' and data and not html_body:
            html_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        
        # Recurse into parts
        for sub_part in part.get('parts', []):
            extract_parts(sub_part)
    
    extract_parts(payload)
    return text_body, html_body


def fetch_emails(
    account: str,
    query: str = "",
    limit: int = 20
) -> List[Dict]:
    """Fetch emails from a Gmail account."""
    print(f"\n📥 Fetching from {account}...")
    
    try:
        service = get_gmail_service(account)
    except Exception as e:
        print(f"   ❌ Auth error: {e}")
        return []
    
    try:
        # Get message list
        results = service.users().messages().list(
            userId='me',
            maxResults=limit,
            q=query
        ).execute()
        
        messages = results.get('messages', [])
        if not messages:
            print(f"   ⚠️  No messages found")
            return []
        
        print(f"   Found {len(messages)} messages")
        
        emails = []
        for msg_info in messages:
            try:
                msg = service.users().messages().get(
                    userId='me',
                    id=msg_info['id'],
                    format='full'
                ).execute()
                
                # Parse headers
                headers = {h['name'].lower(): h['value'] for h in msg['payload'].get('headers', [])}
                
                from_name, from_email = parse_email_address(headers.get('from', ''))
                _, to_email = parse_email_address(headers.get('to', ''))
                
                # Get body
                text_body, html_body = get_body_from_payload(msg['payload'])
                
                # Check for attachments
                has_attachments = False
                for part in msg['payload'].get('parts', []):
                    if part.get('filename'):
                        has_attachments = True
                        break
                
                emails.append({
                    'gmail_id': msg['id'],
                    'thread_id': msg.get('threadId'),
                    'account': account,
                    'from_email': from_email or 'unknown',
                    'from_name': from_name,
                    'to_email': to_email,
                    'subject': headers.get('subject'),
                    'snippet': msg.get('snippet'),
                    'body_text': text_body,
                    'body_html': html_body,
                    'date': headers.get('date', ''),
                    'labels': ','.join(msg.get('labelIds', [])),
                    'has_attachments': has_attachments
                })
                
            except Exception as e:
                print(f"   ⚠️  Error fetching message {msg_info['id']}: {e}")
                continue
        
        return emails
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []


def show_inbox(account: Optional[str] = None, limit: int = 20):
    """Show emails needing responses."""
    emails = get_unresponded_emails(account=account, limit=limit)
    
    if not emails:
        print("\n✨ Inbox empty! No emails need responses.")
        return
    
    print(f"\n📥 Unresponded Emails ({len(emails)} total):\n")
    print("-" * 80)
    
    for em in emails:
        print(f"\n  ID: {em['id']}  |  {em['account']}  |  {em['date'][:20] if em['date'] else 'unknown'}")
        print(f"  From: {em['from_name'] or ''} <{em['from_email']}>")
        print(f"  Subject: {em['subject'] or '(no subject)'}")
        snippet = em['snippet'] or '(no preview)'
        if len(snippet) > 150:
            snippet = snippet[:150] + "..."
        print(f"  Preview: {snippet}")
        print("-" * 80)
    
    print(f"\n💡 To view full email: python fetch.py --show <ID>")


def show_email(email_id: int):
    """Show full email details."""
    em = get_email_by_id(email_id)
    if not em:
        print(f"❌ Email with ID {email_id} not found")
        return
    
    print(f"\n📨 Email Details:")
    print(f"   DB ID: {em['id']}")
    print(f"   Gmail ID: {em['gmail_id']}")
    print(f"   Account: {em['account']}")
    print(f"   From: {em['from_name'] or ''} <{em['from_email']}>")
    print(f"   To: {em['to_email']}")
    print(f"   Subject: {em['subject']}")
    print(f"   Date: {em['date']}")
    print(f"   Labels: {em['labels']}")
    print(f"   Attachments: {'Yes' if em['has_attachments'] else 'No'}")
    print(f"   Responded: {'Yes' if em['responded'] else 'No'}")
    print(f"\n{'='*60}")
    print(f"BODY:\n")
    print(em['body_text'] or em['snippet'] or '(no content)')
    print(f"\n{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch emails from Gmail and store in database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("--account", type=str, help="Specific account to fetch from")
    parser.add_argument("--limit", type=int, default=20, help="Max messages to fetch (default: 20)")
    parser.add_argument("--query", type=str, default="", help="Gmail search query (e.g., 'is:unread')")
    parser.add_argument("--inbox", action="store_true", help="Show unresponded emails")
    parser.add_argument("--show", type=int, metavar="ID", help="Show full email by ID")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--no-db", action="store_true", help="Skip saving to database")
    
    args = parser.parse_args()
    
    # Initialize database
    init_db()
    
    if args.stats:
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
        return
    
    if args.inbox:
        show_inbox(account=args.account, limit=args.limit)
        return
    
    if args.show:
        show_email(args.show)
        return
    
    # Fetch emails
    accounts = [args.account] if args.account else get_all_accounts()
    
    all_emails = []
    for account in accounts:
        emails = fetch_emails(account, query=args.query, limit=args.limit)
        all_emails.extend(emails)
        if emails:
            print(f"   ✓ Fetched {len(emails)} emails from {account}")
    
    if not all_emails:
        print("\n⚠️  No emails fetched")
        return
    
    # Save to database
    if not args.no_db:
        result = save_emails_batch(all_emails)
        print(f"\n💾 Database: {result['new']} new, {result['duplicate']} duplicates skipped")
    
    print(f"\n📊 Total emails fetched: {len(all_emails)}")
    print(f"\n💡 View inbox: python fetch.py --inbox")


if __name__ == "__main__":
    main()
