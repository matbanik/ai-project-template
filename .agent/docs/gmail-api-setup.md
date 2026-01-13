# Gmail API Setup Guide

Complete guide for setting up Gmail API OAuth2 credentials for the email tools, including support for personal Gmail and Google Workspace accounts.

## Quick Start

If you already have OAuth credentials:

```bash
# Add account interactively
python tools/email/auth.py --add

# Or directly in api-keys.json
# Then authenticate
python tools/email/auth.py <account_name>
```

## Prerequisites

- A Google account (personal Gmail or Google Workspace)
- Access to Google Cloud Console

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top → **New Project**
3. Enter project name (e.g., `gmail-email-tools`)
4. Click **Create**
5. Wait for project to be created, then select it

**Note**: You can reuse an existing project if you have one.

## Step 2: Enable Gmail API

1. In your project, go to **APIs & Services** → **Library**
2. Search for "Gmail API"
3. Click on **Gmail API**
4. Click **Enable**

## Step 3: Configure OAuth Consent Screen

This step is **required** before creating credentials.

### For Personal Gmail Accounts

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** user type → **Create**
3. Fill in required fields:
   - **App name**: `Email Tools` (or your choice)
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Click **Save and Continue**
5. **Scopes**: Click **Add or Remove Scopes**
   - Search for `gmail.readonly`
   - Select `https://www.googleapis.com/auth/gmail.readonly`
   - Click **Update** → **Save and Continue**
6. **Test users**: Click **Add Users**
   - Add your Gmail address
   - Click **Save and Continue**
7. Review and click **Back to Dashboard**

### For Google Workspace Accounts

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **Internal** user type → **Create**
   - Internal means only users in your Workspace organization can use it
   - No test user limits
3. Fill in required fields same as above
4. Add the `gmail.readonly` scope
5. **Save and Continue** through all steps

## Step 4: Create OAuth2 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Select application type:
   - **Desktop app** for personal Gmail accounts
   - **Web application** for Google Workspace (optional, Desktop also works)
4. Enter a name (e.g., `Email Tools Desktop`)
5. Click **Create**
6. A dialog shows your **Client ID** and **Client Secret**
7. **Copy both values** - you'll need them for `api-keys.json`

> **Important**: You can also click **Download JSON** to save credentials locally, but the new system stores them in `api-keys.json` instead.

## Step 5: Add Account to api-keys.json

### Option A: Interactive CLI

```bash
python tools/email/auth.py --add
```

Follow the prompts:
- Account name (e.g., `personal`, `work`, `company`)
- Client ID
- Client Secret
- Project ID (optional)
- Is Google Workspace? (y/N)

### Option B: Manual Edit

Add to `api-keys.json`:

```json
{
  "gmail_accounts": {
    "your_account_name": {
      "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
      "client_secret": "GOCSPX-...",
      "project_id": "your-project-id",
      "is_workspace": false,
      "_comment": "Description of this account"
    }
  }
}
```

**For Google Workspace accounts**, set `"is_workspace": true`.

## Step 6: Authenticate

Run authentication for your account:

```bash
python tools/email/auth.py your_account_name
```

This will:
1. Open a browser window
2. Ask you to sign in to your Google account
3. Ask you to authorize the app to read your email
4. Save the token back to `api-keys.json` automatically

### First-Time Authorization Flow

1. Browser opens to Google sign-in
2. Select the Google account you want to authorize
3. You may see "Google hasn't verified this app" warning:
   - Click **Advanced**
   - Click **Go to [App Name] (unsafe)**
4. Review permissions (read-only access to Gmail)
5. Click **Allow**
6. Browser shows "The authentication flow has completed"
7. Return to terminal - credentials are saved

## Google Workspace: Additional Considerations

### Domain-Wide Delegation (Optional)

For enterprise scenarios where you need to access multiple users' mailboxes:

1. Go to **APIs & Services** → **Credentials**
2. Create a **Service Account** instead of OAuth2
3. In Workspace Admin Console, authorize the service account
4. Use service account credentials in your code

> **Note**: This requires Workspace admin privileges and is beyond the scope of the current email tools.

### Workspace Admin Approval

If your Workspace admin requires app approval:

1. Share your OAuth consent screen details with admin
2. Admin goes to **Admin Console** → **Security** → **API controls** → **App access control**
3. Admin approves your app

### Troubleshooting Workspace Access

| Issue | Solution |
|-------|----------|
| "Access blocked: App not verified" | Use Internal user type or get admin approval |
| "This app is blocked" | Contact Workspace admin |
| "Unauthorized client" | Check client_id matches exactly |
| Port in use error | Set `is_workspace: true` to use port 8080 |

## Managing Accounts

### List Configured Accounts

```bash
python tools/email/auth.py --list
```

Output shows:
- Account name
- `[Workspace]` tag if is_workspace=true
- `✓` if token exists, `(needs auth)` otherwise

### Remove Token (Force Re-authentication)

```bash
python tools/email/auth.py --remove-token account_name
```

### Migrate from Legacy Pickle Files

If you have existing `token.pickle` files:

```bash
python tools/email/auth.py account_name --migrate path/to/token.pickle
```

## Security Best Practices

1. **Never commit** `api-keys.json` to version control
2. **Use read-only scope** (`gmail.readonly`) - the tools only read email
3. **Rotate secrets** periodically in Google Cloud Console
4. **Remove unused accounts** from `api-keys.json`
5. **Monitor access** in Google Account security settings

## Troubleshooting

### "redirect_uri_mismatch" Error

**Cause**: OAuth redirect URI doesn't match configuration.

**Solution**:
1. Go to Google Cloud Console → Credentials
2. Edit your OAuth client
3. Add `http://localhost` (and `http://localhost:8080` for Workspace)
4. Save and try again

### "access_denied" or "unauthorized_client"

**Cause**: User not in test users list, or app not approved.

**Solution**:
1. Go to OAuth consent screen
2. Add your email to test users
3. Or publish the app (requires verification)

### Token Refresh Errors

**Cause**: Refresh token expired or revoked.

**Solution**:
```bash
python tools/email/auth.py --remove-token account_name
python tools/email/auth.py account_name  # Re-authenticate
```

### "File not found: api-keys.json"

**Cause**: Running from wrong directory or file missing.

**Solution**: Ensure you're in project root and `api-keys.json` exists.

## API Quotas

Gmail API has these default quotas:

| Quota | Limit |
|-------|-------|
| Queries per day | 1,000,000,000 |
| Queries per 100 seconds per user | 250 |
| Messages.list per day | 500,000 |
| Messages.get per day | 500,000 |

For most personal use, you'll never hit these limits.

## Related Files

| File | Purpose |
|------|---------|
| `api-keys.json` | Stores OAuth credentials and tokens |
| `tools/email/auth.py` | Authentication module |
| `tools/email/fetch.py` | Email fetching script |
| `tools/email/main.py` | Main orchestration script |

## Example: Adding a New Workspace Account

```bash
# 1. Create credentials in Google Cloud Console (steps 1-4)

# 2. Add account
python tools/email/auth.py --add --workspace
# Enter: work
# Enter: 123456-abc.apps.googleusercontent.com
# Enter: GOCSPX-xxx
# Enter: my-project-id

# 3. Authenticate
python tools/email/auth.py work
# Browser opens, authorize access

# 4. Verify
python tools/email/auth.py --list
# Output: work [Workspace] ✓

# 5. Use in scripts
python tools/email/fetch.py --account work --limit 10
```

## Configuration Reference

### Account Configuration Schema

```json
{
  "gmail_accounts": {
    "<account_name>": {
      "client_id": "required - OAuth2 client ID",
      "client_secret": "required - OAuth2 client secret",
      "project_id": "optional - Google Cloud project ID",
      "is_workspace": "optional - true for Workspace accounts",
      "token": {
        "auto-populated after first authentication"
      },
      "_comment": "optional - description for humans"
    }
  }
}
```

### Scopes Used

| Scope | Purpose |
|-------|---------|
| `gmail.readonly` | Read-only access to email messages and labels |

To add more scopes (e.g., send email), update `SCOPES` in `auth.py` and re-authenticate all accounts.
