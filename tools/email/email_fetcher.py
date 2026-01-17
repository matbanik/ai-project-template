"""
Email fetcher module for Gmail API.
Handles pagination, rate limiting, and email parsing.
"""

import base64
import time
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Generator, Optional

from googleapiclient.errors import HttpError

# Rate limiting settings
MAX_REQUESTS_PER_SECOND = 10
REQUEST_INTERVAL = 1.0 / MAX_REQUESTS_PER_SECOND
MAX_RETRIES = 5
INITIAL_BACKOFF = 1.0


class RateLimiter:
    """Simple rate limiter to avoid hitting API quotas."""

    def __init__(self, interval: float = REQUEST_INTERVAL):
        self.interval = interval
        self.last_request = 0.0

    def wait(self):
        """Wait if needed to respect rate limit."""
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed)
        self.last_request = time.time()


def exponential_backoff(func, *args, **kwargs):
    """Execute a function with exponential backoff on rate limit errors."""
    backoff = INITIAL_BACKOFF

    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            if e.resp.status == 429:  # Rate limit exceeded
                wait_time = backoff * (2 ** attempt)
                print(f"Rate limit hit. Waiting {wait_time:.1f}s before retry {attempt + 1}/{MAX_RETRIES}...")
                time.sleep(wait_time)
            else:
                raise

    raise Exception(f"Max retries ({MAX_RETRIES}) exceeded")


def get_label_id(service, label_name: str) -> Optional[str]:
    """
    Get the label ID for a given label name.

    Args:
        service: Gmail API service object
        label_name: Name of the label to find

    Returns:
        Label ID or None if not found
    """
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    for label in labels:
        if label['name'].lower() == label_name.lower():
            return label['id']

    return None


def list_message_ids(service, label_id: str, rate_limiter: RateLimiter) -> Generator[str, None, None]:
    """
    List all message IDs with the specified label, handling pagination.

    Args:
        service: Gmail API service object
        label_id: Label ID to filter by
        rate_limiter: Rate limiter instance

    Yields:
        Message IDs
    """
    page_token = None
    total_fetched = 0

    while True:
        rate_limiter.wait()

        # Fetch page of message IDs
        request = service.users().messages().list(
            userId='me',
            labelIds=[label_id],
            maxResults=100,  # Max allowed
            pageToken=page_token
        )

        results = exponential_backoff(request.execute)
        messages = results.get('messages', [])

        for msg in messages:
            yield msg['id']
            total_fetched += 1

        print(f"Fetched {total_fetched} message IDs so far...")

        # Check for next page
        page_token = results.get('nextPageToken')
        if not page_token:
            break

    print(f"Total message IDs found: {total_fetched}")


def parse_email_date(date_str: str) -> datetime:
    """Parse email date header to datetime."""
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        # Fallback to current time if parsing fails
        return datetime.now()


def extract_body(payload: dict) -> str:
    """
    Extract plain text body from email payload.
    Falls back to HTML if plain text not available.

    Args:
        payload: Email payload from Gmail API

    Returns:
        Email body as plain text
    """
    # Check for direct body
    if payload.get('body', {}).get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='replace')

    # Check multipart structure
    parts = payload.get('parts', [])

    # First pass: look for plain text
    for part in parts:
        mime_type = part.get('mimeType', '')

        if mime_type == 'text/plain':
            data = part.get('body', {}).get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')

        # Recursively check nested parts
        if 'parts' in part:
            result = extract_body(part)
            if result:
                return result

    # Second pass: fall back to HTML
    for part in parts:
        mime_type = part.get('mimeType', '')

        if mime_type == 'text/html':
            data = part.get('body', {}).get('data')
            if data:
                html = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
                # Basic HTML stripping for analytics
                import re
                text = re.sub(r'<[^>]+>', ' ', html)
                text = re.sub(r'\s+', ' ', text)
                return text.strip()

    return ""


def get_header(headers: list, name: str) -> str:
    """Get a specific header value from headers list."""
    for header in headers:
        if header['name'].lower() == name.lower():
            return header['value']
    return ""


def fetch_email_details(service, message_id: str, rate_limiter: RateLimiter) -> dict:
    """
    Fetch full details of a single email.

    Args:
        service: Gmail API service object
        message_id: Gmail message ID
        rate_limiter: Rate limiter instance

    Returns:
        Dict with: id, sender, subject, body, timestamp
    """
    rate_limiter.wait()

    request = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full'
    )

    msg = exponential_backoff(request.execute)

    headers = msg.get('payload', {}).get('headers', [])

    sender = get_header(headers, 'From')
    subject = get_header(headers, 'Subject')
    date_str = get_header(headers, 'Date')

    timestamp = parse_email_date(date_str)
    body = extract_body(msg.get('payload', {}))

    return {
        'id': message_id,
        'sender': sender,
        'subject': subject,
        'body': body,
        'timestamp': timestamp
    }


def fetch_emails_by_label(service, label_name: str, existing_ids: set[str] = None) -> Generator[dict, None, None]:
    """
    Fetch all emails with given label, skipping already-fetched ones.

    Args:
        service: Gmail API service object
        label_name: Name of the label to filter by
        existing_ids: Set of email IDs already in database (for incremental sync)

    Yields:
        Email dicts with: id, sender, subject, body, timestamp
    """
    existing_ids = existing_ids or set()
    rate_limiter = RateLimiter()

    # Get label ID
    label_id = get_label_id(service, label_name)
    if not label_id:
        print(f"ERROR: Label '{label_name}' not found!")
        print("Available labels:")
        results = service.users().labels().list(userId='me').execute()
        for label in results.get('labels', []):
            print(f"  - {label['name']}")
        return

    print(f"Found label '{label_name}' with ID: {label_id}")

    # Fetch message IDs
    skipped = 0
    fetched = 0

    for message_id in list_message_ids(service, label_id, rate_limiter):
        # Skip if already in database (incremental sync)
        if message_id in existing_ids:
            skipped += 1
            continue

        try:
            email_data = fetch_email_details(service, message_id, rate_limiter)
            fetched += 1

            if fetched % 10 == 0:
                print(f"Fetched {fetched} new emails (skipped {skipped} existing)...")

            yield email_data

        except Exception as e:
            print(f"Error fetching message {message_id}: {e}")
            continue

    print(f"Fetching complete: {fetched} new, {skipped} skipped")
