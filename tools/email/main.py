"""
Main orchestration script for Gmail email fetcher.

Fetches social notification emails from one or more Gmail accounts.
Supports incremental sync - only fetches new emails on subsequent runs.
Enriches emails with platform detection and notification type classification.

Usage:
    python main.py                           # Fetch from all accounts
    python main.py --account matbanik        # Fetch from specific account
    python main.py --label "MyLabel"         # Use custom label
    python main.py --all                     # Fetch from all accounts (default)

First run:
    - Opens browser for OAuth2 authorization (per account)
    - Fetches all emails with specified label
    - Stores in emails.db with platform enrichment

Subsequent runs:
    - Uses cached credentials
    - Only fetches new emails not already in database
"""

import argparse
from datetime import datetime

from auth import get_gmail_service, get_all_accounts
from database import (
    init_database,
    get_existing_ids,
    upsert_emails_batch,
    get_email_count,
    set_last_sync_timestamp,
    get_last_sync_timestamp
)
from email_fetcher import fetch_emails_by_label
from platforms import enrich_email

# Default label for social notifications
DEFAULT_LABEL = "Social Notifications"

# Batch size for database inserts
BATCH_SIZE = 50


def sync_account(account: str, label_name: str, existing_ids: set) -> dict:
    """
    Sync emails from a single account.
    
    Args:
        account: Account name
        label_name: Gmail label to fetch
        existing_ids: Set of existing email IDs
        
    Returns:
        Dict with sync stats
    """
    print(f"\n--- Syncing account: {account} ---")
    
    try:
        service = get_gmail_service(account)
    except Exception as e:
        print(f"  Error authenticating: {e}")
        return {"account": account, "new": 0, "error": str(e)}
    
    batch = []
    total_new = 0
    platform_counts = {}
    
    for email_data in fetch_emails_by_label(service, label_name, existing_ids):
        # Enrich with platform detection + account info
        enriched = enrich_email(email_data)
        enriched['account'] = account
        batch.append(enriched)
        
        # Track platform counts
        platform = enriched.get("platform", "unknown")
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Insert in batches for efficiency
        if len(batch) >= BATCH_SIZE:
            upsert_emails_batch(batch)
            total_new += len(batch)
            print(f"  Saved batch of {len(batch)} emails (total new: {total_new})")
            batch = []
    
    # Insert remaining emails
    if batch:
        upsert_emails_batch(batch)
        total_new += len(batch)
        print(f"  Saved final batch of {len(batch)} emails")
    
    return {
        "account": account,
        "new": total_new,
        "platforms": platform_counts,
        "error": None
    }


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Fetch and classify social notification emails from Gmail"
    )
    parser.add_argument(
        "--account", "-a",
        default=None,
        help="Specific account to sync (default: all accounts)"
    )
    parser.add_argument(
        "--label", "-l",
        default=DEFAULT_LABEL,
        help=f"Gmail label to fetch (default: '{DEFAULT_LABEL}')"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="Sync all accounts (default behavior)"
    )
    args = parser.parse_args()
    
    label_name = args.label
    
    # Determine which accounts to sync
    if args.account:
        accounts = [args.account]
    else:
        accounts = get_all_accounts()

    print("=" * 60)
    print("Gmail Email Fetcher - Multi-Account Social Notifications")
    print("=" * 60)
    print(f"Accounts: {', '.join(accounts)}")
    print(f"Label: {label_name}")
    
    # Initialize database
    print("\n[1/3] Initializing database...")
    init_database()
    
    initial_count = get_email_count()
    print(f"Current email count: {initial_count}")
    
    last_sync = get_last_sync_timestamp()
    if last_sync:
        print(f"Last sync: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get existing IDs for incremental sync (shared across accounts)
    print("\n[2/3] Checking for existing emails...")
    existing_ids = get_existing_ids()
    print(f"Found {len(existing_ids)} existing emails in database")
    
    # Sync each account
    print(f"\n[3/3] Fetching emails with label '{label_name}'...")
    
    all_results = []
    for account in accounts:
        result = sync_account(account, label_name, existing_ids)
        all_results.append(result)
    
    # Update sync timestamp
    set_last_sync_timestamp(datetime.now())
    
    # Summary
    final_count = get_email_count()
    total_new = sum(r["new"] for r in all_results)
    
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    
    for result in all_results:
        status = "✓" if not result.get("error") else "✗"
        print(f"  {status} {result['account']:15s} {result['new']:5d} new emails")
        if result.get("platforms"):
            for platform, count in sorted(result["platforms"].items(), key=lambda x: -x[1]):
                print(f"      {platform:20s} {count}")
    
    print("-" * 60)
    print(f"Total new emails:  {total_new}")
    print(f"Total in database: {final_count}")
    print(f"Database file:     emails.db")
    print("=" * 60)
    
    # Sample query with platform info
    if final_count > 0:
        print("\nSample query - most recent 5 emails:")
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT platform, notification_type, subject, datetime(timestamp) as ts
            FROM emails
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        for row in cursor.fetchall():
            subject = row['subject'][:40] + '...' if row['subject'] and len(row['subject']) > 40 else row['subject']
            print(f"  [{row['platform']:12s}] [{row['notification_type']:8s}] {subject}")
        conn.close()


if __name__ == '__main__':
    main()
