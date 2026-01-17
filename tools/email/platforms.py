"""
Platform mapping module for social email notifications.
Maps email senders to platforms and extracts notification metadata.
"""

from typing import Optional, Dict, Any
import re

# =============================================================================
# SENDER TO PLATFORM MAPPING
# =============================================================================

SENDER_PATTERNS: Dict[str, str] = {
    # Blogging Platforms
    "noreply@tradingview.com": "tradingview",
    "noreply@medium.com": "medium",
    "hello@substack.com": "substack",
    "notify@dev.to": "devto",
    "noreply@hashnode.com": "hashnode",
    "no-reply@blogger.com": "blogger",
    "contact@hackernoon.com": "hackernoon",

    # Social Media
    "messages-noreply@linkedin.com": "linkedin",
    "noreply@discordapp.com": "discord",
    "noreply@youtube.com": "youtube",
    "noreply@redditmail.com": "reddit",
    "notifications@github.com": "github",
    "notification@facebookmail.com": "facebook",
    "notify@x.com": "x",
    "security@mail.instagram.com": "instagram",

    # Newsletter
    "buttondown": "buttondown",  # Pattern match
}

# Regex patterns for partial matches
SENDER_REGEX: Dict[str, str] = {
    r".*@mail\.tradingview\.com": "tradingview",
    r".*@email\.medium\.com": "medium",
    r".*substack.*": "substack",
    r".*linkedin\.com": "linkedin",
    r".*discord(app)?\.com": "discord",
    r".*youtube\.com": "youtube",
    r".*reddit.*": "reddit",
    r".*github\.com": "github",
    r".*facebook.*": "facebook",
    r".*@(x|twitter)\.com": "x",
    r".*buttondown.*": "buttondown",
    r".*instagram\.com": "instagram",
    r".*hashnode.*": "hashnode",
}


# =============================================================================
# NOTIFICATION TYPE DETECTION
# =============================================================================

NOTIFICATION_KEYWORDS: Dict[str, list] = {
    "comment": ["comment", "commented", "left a comment", "new comment"],
    "reply": ["reply", "replied", "response", "responded"],
    "mention": ["mention", "mentioned", "tagged"],
    "like": ["like", "liked", "reaction", "reacted", "upvote"],
    "follow": ["follow", "following", "new follower", "subscribed"],
    "dm": ["direct message", "dm", "private message", "sent you a message"],
    "share": ["share", "shared", "repost", "reposted"],
}


# =============================================================================
# FUNCTIONS
# =============================================================================

def detect_platform(sender: str) -> str:
    """
    Detect platform from email sender address.

    Args:
        sender: Full sender string (e.g., "TradingView <noreply@tradingview.com>")

    Returns:
        Platform identifier or 'unknown'
    """
    sender_lower = sender.lower()

    # First, try exact matches
    for pattern, platform in SENDER_PATTERNS.items():
        if pattern.lower() in sender_lower:
            return platform

    # Then try regex patterns
    for pattern, platform in SENDER_REGEX.items():
        if re.search(pattern, sender_lower, re.IGNORECASE):
            return platform

    return "unknown"


def detect_notification_type(subject: str, body: str = "") -> str:
    """
    Detect notification type from subject and body.

    Args:
        subject: Email subject
        body: Email body (optional)

    Returns:
        Notification type (comment, reply, mention, like, follow, dm, share, or general)
    """
    text = f"{subject} {body}".lower()

    for ntype, keywords in NOTIFICATION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return ntype

    return "general"


def extract_urls(body: str) -> list[str]:
    """
    Extract URLs from email body.

    Args:
        body: Email body text

    Returns:
        List of URLs found
    """
    url_pattern = r'https?://[^\s<>"\']+(?=[<>"\'\s]|$)'
    return re.findall(url_pattern, body)


def extract_original_post_url(body: str, platform: str) -> Optional[str]:
    """
    Extract the URL of the original post being commented on.

    Args:
        body: Email body
        platform: Platform identifier

    Returns:
        Original post URL or None
    """
    urls = extract_urls(body)

    # Platform-specific URL patterns
    patterns = {
        "tradingview": r"tradingview\.com/(chart|i)/",
        "medium": r"medium\.com/.+/[a-z0-9-]+",
        "substack": r"substack\.com/p/",
        "linkedin": r"linkedin\.com/(posts|feed/update)/",
        "youtube": r"youtube\.com/watch\?v=|youtu\.be/",
        "reddit": r"reddit\.com/r/.+/comments/",
        "devto": r"dev\.to/.+/[a-z0-9-]+",
        "github": r"github\.com/.+/(issues|discussions|pull)/",
    }

    pattern = patterns.get(platform)
    if pattern:
        for url in urls:
            if re.search(pattern, url, re.IGNORECASE):
                return url

    # Fallback: return first URL that isn't unsubscribe/settings
    for url in urls:
        if not any(x in url.lower() for x in ['unsubscribe', 'settings', 'manage', 'preferences']):
            return url

    return None


def enrich_email(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich email data with platform detection and extracted metadata.

    Args:
        email_data: Dict with sender, subject, body

    Returns:
        Enriched dict with platform, notification_type, original_url
    """
    sender = email_data.get("sender", "")
    subject = email_data.get("subject", "")
    body = email_data.get("body", "")

    platform = detect_platform(sender)
    notification_type = detect_notification_type(subject, body)
    original_url = extract_original_post_url(body, platform)

    return {
        **email_data,
        "platform": platform,
        "notification_type": notification_type,
        "original_url": original_url,
    }


# =============================================================================
# PLATFORM METADATA
# =============================================================================

# Platform metadata - customize profile_url for your accounts
# Set profile_url to None or your own profile URLs
PLATFORM_INFO = {
    "tradingview": {
        "name": "TradingView",
        "profile_url": None,  # e.g., "https://www.tradingview.com/u/YOUR_USERNAME/"
        "has_api": False,
        "color": "#2962FF",
    },
    "medium": {
        "name": "Medium",
        "profile_url": None,  # e.g., "https://medium.com/@your_username"
        "has_api": False,
        "color": "#000000",
    },
    "substack": {
        "name": "Substack",
        "profile_url": None,  # e.g., "https://yourname.substack.com/"
        "has_api": False,
        "color": "#FF6719",
    },
    "linkedin": {
        "name": "LinkedIn",
        "profile_url": None,  # e.g., "https://www.linkedin.com/in/your-profile/"
        "has_api": True,  # Limited
        "color": "#0A66C2",
    },
    "discord": {
        "name": "Discord",
        "profile_url": None,  # e.g., "https://discord.gg/your-server"
        "has_api": True,
        "color": "#5865F2",
    },
    "youtube": {
        "name": "YouTube",
        "profile_url": None,  # e.g., "https://www.youtube.com/@your_channel"
        "has_api": True,
        "color": "#FF0000",
    },
    "devto": {
        "name": "Dev.to",
        "profile_url": None,  # e.g., "https://dev.to/your_username"
        "has_api": True,
        "color": "#0A0A0A",
    },
    "reddit": {
        "name": "Reddit",
        "profile_url": None,  # e.g., "https://reddit.com/u/your_username/"
        "has_api": True,
        "color": "#FF4500",
    },
    "github": {
        "name": "GitHub",
        "profile_url": None,  # e.g., "https://github.com/your_username/"
        "has_api": True,
        "color": "#181717",
    },
    "hashnode": {
        "name": "Hashnode",
        "profile_url": None,  # e.g., "https://your_username.hashnode.dev/"
        "has_api": True,
        "color": "#2962FF",
    },
    "blogger": {
        "name": "Blogger",
        "profile_url": None,  # e.g., "https://your-blog.blogspot.com/"
        "has_api": True,
        "color": "#FF5722",
    },
    "buttondown": {
        "name": "Buttondown",
        "profile_url": None,  # e.g., "https://buttondown.com/your_newsletter"
        "has_api": True,
        "color": "#0069FF",
    },
    "x": {
        "name": "X (Twitter)",
        "profile_url": None,  # e.g., "https://x.com/your_handle"
        "has_api": True,
        "color": "#000000",
    },
    "facebook": {
        "name": "Facebook",
        "profile_url": None,  # e.g., "https://www.facebook.com/your.profile/"
        "has_api": True,
        "color": "#1877F2",
    },
    "instagram": {
        "name": "Instagram",
        "profile_url": None,  # e.g., "https://www.instagram.com/your_username/"
        "has_api": False,  # Unofficial only
        "color": "#E4405F",
    },
}


if __name__ == "__main__":
    # Test the module
    test_cases = [
        ("TradingView <noreply@tradingview.com>", "New comment on your idea"),
        ("Medium Daily Digest <noreply@medium.com>", "Someone replied to your story"),
        ("LinkedIn <messages-noreply@linkedin.com>", "John Doe mentioned you"),
    ]

    for sender, subject in test_cases:
        platform = detect_platform(sender)
        ntype = detect_notification_type(subject)
        print(f"{sender[:30]:30s} → Platform: {platform:15s} Type: {ntype}")
