# Email Policy Configuration Guide

This guide explains how to configure the email fetching policy in `tools/email/email_policy.json`.

## Quick Start

```bash
# View current policy
python tools/email/policy.py --show

# Validate policy file
python tools/email/policy.py --validate

# Test sender platform detection
python tools/email/policy.py --test-sender "noreply@github.com"

# Test subject notification type
python tools/email/policy.py --test-subject "Someone replied to your comment"
```

## Policy File Structure

```json
{
  "_schema_version": "1.0",
  "global": { ... },
  "gmail_accounts": { ... },
  "microsoft_accounts": { ... },
  "sender_platform_mappings": { ... },
  "notification_type_keywords": { ... }
}
```

## Global Settings

Global settings apply to all accounts unless overridden per-account.

```json
{
  "global": {
    "enabled": true,
    "max_emails_per_sync": 500,
    "batch_size": 50,
    "skip_duplicates": true,
    "incremental_sync": true,
    "date_range": {
      "enabled": false,
      "after": null,
      "before": null,
      "last_days": null
    },
    "read_status": "all",
    "has_attachments": null,
    "enrich_platform": true,
    "enrich_notification_type": true,
    "extract_urls": true
  }
}
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | bool | `true` | Master switch for email fetching |
| `max_emails_per_sync` | int | `500` | Maximum emails to fetch per sync |
| `batch_size` | int | `50` | Batch size for database inserts |
| `skip_duplicates` | bool | `true` | Skip emails already in database |
| `incremental_sync` | bool | `true` | Only fetch new emails since last sync |
| `read_status` | string | `"all"` | Filter by read status: `"all"`, `"read"`, `"unread"` |
| `has_attachments` | bool/null | `null` | Filter by attachments: `true`, `false`, or `null` (any) |
| `enrich_platform` | bool | `true` | Detect platform from sender |
| `enrich_notification_type` | bool | `true` | Detect notification type from subject |
| `extract_urls` | bool | `true` | Extract URLs from email body |

### Date Range Settings

```json
"date_range": {
  "enabled": true,
  "last_days": 30
}
```

| Setting | Type | Description |
|---------|------|-------------|
| `enabled` | bool | Enable date filtering |
| `last_days` | int | Fetch emails from last N days |
| `after` | string | ISO date - fetch emails after this date |
| `before` | string | ISO date - fetch emails before this date |

Examples:
```json
// Last 7 days
"date_range": { "enabled": true, "last_days": 7 }

// Specific range
"date_range": { "enabled": true, "after": "2026-01-01T00:00:00Z", "before": "2026-01-31T23:59:59Z" }

// After a specific date
"date_range": { "enabled": true, "after": "2026-01-01T00:00:00Z" }
```

## Account Configuration

### Gmail Accounts

```json
{
  "gmail_accounts": {
    "account_name": {
      "enabled": true,
      "folders": {
        "include": ["Social Notifications"],
        "exclude": []
      },
      "senders": {
        "include_patterns": [],
        "exclude_patterns": [".*@promotions\\..*"]
      },
      "subjects": {
        "include_patterns": [],
        "exclude_patterns": ["^Unsubscribe.*"]
      },
      "platforms": {
        "include": [],
        "exclude": ["facebook"]
      },
      "notification_types": {
        "include": ["comment", "reply", "mention"],
        "exclude": []
      },
      "date_range": {
        "enabled": true,
        "last_days": 30
      },
      "read_status": "unread",
      "max_emails_per_sync": 100
    }
  }
}
```

### Microsoft Accounts

```json
{
  "microsoft_accounts": {
    "olaplex": {
      "enabled": true,
      "folders": {
        "include": ["Inbox", "Security", "Security/EDR-Alerts"],
        "exclude": ["Junk Email", "Deleted Items"]
      },
      "senders": {
        "include_patterns": [],
        "exclude_patterns": [".*newsletter.*"]
      },
      "subjects": {
        "include_patterns": [".*alert.*", ".*security.*"],
        "exclude_patterns": []
      },
      "date_range": {
        "enabled": true,
        "last_days": 30
      }
    }
  }
}
```

## Filtering Rules

### How Filtering Works

1. **Folders**: Emails must be in an included folder and not in excluded folders
2. **Senders**: If include patterns specified, sender must match at least one; then exclude patterns checked
3. **Subjects**: Same logic as senders
4. **Platforms**: If include list specified, platform must be in it; then exclude list checked
5. **Notification Types**: Same logic as platforms

### Include vs Exclude Logic

| Include | Exclude | Behavior |
|---------|---------|----------|
| Empty | Empty | Allow all |
| Empty | Has items | Allow all except excluded |
| Has items | Empty | Only allow included |
| Has items | Has items | Must be in include AND not in exclude |

### Regex Patterns

Sender and subject filters use Python regex patterns (case-insensitive):

```json
"exclude_patterns": [
  ".*@promotions\\..*",    // Matches promotions@ subdomain
  ".*no-?reply@.*",        // Matches noreply@ or no-reply@
  "^(Unsubscribe|Newsletter).*"  // Starts with Unsubscribe or Newsletter
]
```

Common patterns:
| Pattern | Matches |
|---------|---------|
| `.*@domain\.com` | Any sender from domain.com |
| `.*newsletter.*` | Contains "newsletter" anywhere |
| `^Alert:.*` | Subject starts with "Alert:" |
| `.*\[urgent\].*` | Contains "[urgent]" |

## Platform Detection

### Exact Matches

```json
{
  "sender_platform_mappings": {
    "exact": {
      "noreply@tradingview.com": "tradingview",
      "noreply@medium.com": "medium",
      "notifications@github.com": "github"
    }
  }
}
```

### Pattern Matches

```json
{
  "sender_platform_mappings": {
    "patterns": {
      ".*@mail\\.tradingview\\.com": "tradingview",
      ".*linkedin\\.com": "linkedin",
      ".*@(x|twitter)\\.com": "x"
    }
  }
}
```

### Adding New Platforms

1. Add exact match if sender email is consistent:
   ```json
   "exact": {
     "noreply@newplatform.com": "newplatform"
   }
   ```

2. Add pattern if sender varies:
   ```json
   "patterns": {
     ".*@.*newplatform\\.com": "newplatform"
   }
   ```

## Notification Type Detection

Keywords that trigger each notification type:

```json
{
  "notification_type_keywords": {
    "comment": ["comment", "commented", "new comment"],
    "reply": ["reply", "replied", "response"],
    "mention": ["mention", "mentioned", "tagged"],
    "like": ["like", "liked", "reaction", "upvote"],
    "follow": ["follow", "following", "subscribed"],
    "dm": ["direct message", "dm", "private message"],
    "share": ["share", "shared", "repost"],
    "alert": ["alert", "warning", "critical", "urgent"],
    "security": ["security", "threat", "vulnerability"]
  }
}
```

### Adding New Types

```json
{
  "notification_type_keywords": {
    "purchase": ["purchase", "order", "receipt", "invoice"],
    "shipping": ["shipped", "delivery", "tracking"]
  }
}
```

## Per-Account Overrides

Any global setting can be overridden at the account level:

```json
{
  "global": {
    "max_emails_per_sync": 500,
    "read_status": "all"
  },
  "gmail_accounts": {
    "personal": {
      "max_emails_per_sync": 100,  // Override: 100 instead of 500
      "read_status": "unread"      // Override: only unread
    },
    "work": {
      // Uses global defaults (500, all)
    }
  }
}
```

## Common Configurations

### Social Media Notifications Only

```json
{
  "gmail_accounts": {
    "personal": {
      "folders": { "include": ["Social Notifications"] },
      "platforms": {
        "include": ["linkedin", "youtube", "github", "x", "reddit"]
      },
      "notification_types": {
        "include": ["comment", "reply", "mention", "like"]
      }
    }
  }
}
```

### Security Alerts Only (Microsoft)

```json
{
  "microsoft_accounts": {
    "work": {
      "folders": {
        "include": ["Inbox", "Security"],
        "exclude": ["Junk Email"]
      },
      "subjects": {
        "include_patterns": [".*alert.*", ".*security.*", ".*threat.*"]
      },
      "notification_types": {
        "include": ["alert", "security"]
      }
    }
  }
}
```

### Exclude Promotional Emails

```json
{
  "gmail_accounts": {
    "personal": {
      "senders": {
        "exclude_patterns": [
          ".*@promotions\\..*",
          ".*marketing@.*",
          ".*newsletter.*",
          ".*noreply@.*\\.google\\.com"
        ]
      },
      "subjects": {
        "exclude_patterns": [
          "^(Unsubscribe|Your weekly digest|Newsletter).*"
        ]
      }
    }
  }
}
```

### Last 7 Days, Unread Only

```json
{
  "gmail_accounts": {
    "urgent": {
      "date_range": { "enabled": true, "last_days": 7 },
      "read_status": "unread",
      "max_emails_per_sync": 50
    }
  }
}
```

## Validation

### Check Policy Syntax

```bash
python tools/email/policy.py --validate
```

### Test Platform Detection

```bash
python tools/email/policy.py --test-sender "GitHub <notifications@github.com>"
# Output: Platform: github
```

### Test Notification Type

```bash
python tools/email/policy.py --test-subject "Someone replied to your comment"
# Output: Notification type: reply
```

## API Usage

```python
from policy import get_policy

policy = get_policy()

# Check if account is enabled
if policy.is_account_enabled('matbanik', 'gmail'):
    # Get folders to fetch
    folders = policy.get_folders('matbanik', 'gmail')
    
    # Get max emails for this account
    max_emails = policy.get_max_emails('matbanik', 'gmail')
    
    # Build Gmail query
    query = policy.build_gmail_query('matbanik')
    
    # Process emails with filtering
    for email in fetch_emails():
        enriched = policy.enrich_email(email)
        
        if policy.filter_email(enriched, 'matbanik', 'gmail'):
            save_to_database(enriched)
```

## Troubleshooting

### Emails Not Being Fetched

1. Check account is enabled: `python policy.py --show`
2. Verify folder names match exactly (case-sensitive)
3. Check sender/subject exclude patterns aren't too broad
4. Verify date range isn't filtering out recent emails

### Wrong Platform Detection

1. Test the sender: `python policy.py --test-sender "sender@domain.com"`
2. Add exact match if pattern isn't working
3. Check regex pattern syntax (escape dots with `\\.`)

### Performance Issues

1. Reduce `max_emails_per_sync` for large mailboxes
2. Enable `date_range` to limit historical fetch
3. Use `read_status: "unread"` if only new emails matter

## Schema Reference

Full JSON Schema for `email_policy.json`:

```json
{
  "_schema_version": "1.0",
  "global": {
    "enabled": boolean,
    "max_emails_per_sync": integer,
    "batch_size": integer,
    "skip_duplicates": boolean,
    "incremental_sync": boolean,
    "date_range": {
      "enabled": boolean,
      "after": string|null,  // ISO date
      "before": string|null, // ISO date
      "last_days": integer|null
    },
    "read_status": "all"|"read"|"unread",
    "has_attachments": boolean|null,
    "enrich_platform": boolean,
    "enrich_notification_type": boolean,
    "extract_urls": boolean
  },
  "gmail_accounts": {
    "<account_name>": {
      "enabled": boolean,
      "folders": {
        "include": [string],
        "exclude": [string]
      },
      "senders": {
        "include_patterns": [regex_string],
        "exclude_patterns": [regex_string]
      },
      "subjects": {
        "include_patterns": [regex_string],
        "exclude_patterns": [regex_string]
      },
      "platforms": {
        "include": [string],
        "exclude": [string]
      },
      "notification_types": {
        "include": [string],
        "exclude": [string]
      },
      "date_range": { ... },
      "read_status": string,
      "max_emails_per_sync": integer
    }
  },
  "microsoft_accounts": { ... },  // Same structure as gmail_accounts
  "sender_platform_mappings": {
    "exact": { "<email>": "<platform>" },
    "patterns": { "<regex>": "<platform>" }
  },
  "notification_type_keywords": {
    "<type>": [keyword_strings]
  }
}
