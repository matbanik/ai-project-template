# Microsoft 365 Email Setup Guide

Complete guide for setting up Microsoft Graph API access to read Microsoft 365 / Exchange Online mailboxes. This guide covers enterprise accounts only (not personal Outlook.com accounts).

## Quick Start

If you already have Entra ID (Azure AD) app credentials:

```bash
# Add account interactively
python tools/email/microsoft_auth.py --add

# Or directly edit api-keys.json, then test
python tools/email/microsoft_auth.py <account_name>
```

## Prerequisites

- Microsoft 365 business/enterprise subscription
- Global Administrator or Application Administrator access to Entra ID
- The mailbox email address you want to access

## Architecture Overview

This setup uses **client credentials flow** (app-only authentication):
- Application authenticates as itself, not as a user
- Requires admin consent to access mailboxes
- No user interaction needed after initial setup
- Ideal for daemon/automated applications

```
Your App → Entra ID → Access Token → Microsoft Graph API → Mailbox
```

## Step 1: Register Application in Entra ID

1. Go to [Microsoft Entra admin center](https://entra.microsoft.com/)
2. Navigate to: **Identity** → **Applications** → **App registrations**
3. Click **+ New registration**
4. Fill in:
   - **Name**: `Email Reader` (or your choice)
   - **Supported account types**: Select "Accounts in this organizational directory only"
   - **Redirect URI**: Leave blank (not needed for client credentials)
5. Click **Register**

After registration, note these values from the **Overview** page:
- **Application (client) ID** → This is your `application_id`
- **Directory (tenant) ID** → This is your `tenant_id`

## Step 2: Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Under **Client secrets**, click **+ New client secret**
3. Add description: `Email Reader Secret`
4. Choose expiration: 24 months (or as per security policy)
5. Click **Add**
6. **IMPORTANT**: Copy the **Value** immediately → This is your `client_secret`
   - You cannot see this value again after leaving this page!

## Step 3: Configure API Permissions

1. Go to **API permissions** in your app registration
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Select **Application permissions** (not Delegated)
5. Add these permissions:
   - `Mail.Read` - Read mail in all mailboxes
   - `User.Read.All` - Read all users' full profiles
6. Click **Add permissions**

### Grant Admin Consent

1. Click **Grant admin consent for [Your Organization]**
2. Confirm by clicking **Yes**
3. Verify all permissions show green checkmarks ✓

| Permission | Type | Status |
|------------|------|--------|
| Mail.Read | Application | ✓ Granted |
| User.Read.All | Application | ✓ Granted |

## Step 4: Configure Application Access Policy (Recommended)

For security, limit which mailboxes the app can access instead of all mailboxes:

### Option A: Application Access Policy (Exchange Admin)

1. Go to [Exchange Admin Center](https://admin.exchange.microsoft.com/)
2. Run PowerShell as Exchange Admin:

```powershell
# Connect to Exchange Online
Connect-ExchangeOnline

# Create mail-enabled security group for allowed mailboxes
New-DistributionGroup -Name "Email Reader Allowed" -Type Security

# Add mailboxes to the group
Add-DistributionGroupMember -Identity "Email Reader Allowed" -Member "mbanik@olaplex.net"

# Create application access policy
New-ApplicationAccessPolicy `
  -AppId "e771827e-3e6f-44d1-b720-1a67b714b403" `
  -PolicyScopeGroupId "Email Reader Allowed" `
  -AccessRight RestrictAccess `
  -Description "Restrict to specific mailboxes"
```

### Option B: Skip (Allow All Mailboxes)

If you're the only admin and trust the app, you can skip this step. The app will have access to all mailboxes in the organization.

## Step 5: Add Account to api-keys.json

### Option A: Interactive CLI

```bash
python tools/email/microsoft_auth.py --add
```

Enter:
- Account name (e.g., `work`, `olaplex`)
- Application (client) ID
- Tenant ID
- Client secret
- Mailbox email (e.g., `user@company.com`)

### Option B: Manual Edit

Add to `api-keys.json`:

```json
{
  "microsoft_accounts": {
    "company": {
      "application_id": "e771827e-3e6f-44d1-b720-1a67b714b403",
      "tenant_id": "2a336a28-086e-4b13-a4b5-e925f12dffc8",
      "client_secret": "T5L8Q~NIuDioHVa7l~...",
      "mailbox": "user@company.com",
      "_comment": "Microsoft 365 enterprise account"
    }
  }
}
```

## Step 6: Test Connection

```bash
python tools/email/microsoft_auth.py company
```

Expected output:
```
Testing account: company
  ✓ Connected to: user@company.com
    Display Name: User Name
    Inbox messages: 1,234
```

## Usage Examples

### List Configured Accounts

```bash
python tools/email/microsoft_auth.py --list
```

### View Recent Emails

```bash
python tools/email/microsoft_auth.py company --emails 5
```

### View Today's Emails

```bash
python tools/email/microsoft_auth.py company --today
```

### View Inbox Rules

```bash
python tools/email/microsoft_auth.py company --rules
```

### View Mail Folders

```bash
python tools/email/microsoft_auth.py company --folders
```

## Accessing Another Mailbox

To access a different mailbox with the same credentials:

### Option 1: Add Separate Account

```bash
python tools/email/microsoft_auth.py --add
# Use same app credentials but different mailbox email
```

### Option 2: Update Mailbox in api-keys.json

```json
"mailbox": "different-user@company.com"
```

Then re-run the test.

## Troubleshooting

### "Insufficient privileges" Error

**Cause**: Admin consent not granted or wrong permission type.

**Solution**:
1. Verify you selected **Application permissions**, not Delegated
2. Click "Grant admin consent" in API permissions
3. Ensure green checkmarks show for all permissions

### "AADSTS7000215: Invalid client secret"

**Cause**: Client secret expired or incorrect.

**Solution**:
1. Go to Certificates & secrets in your app registration
2. Check if secret has expired
3. Create new secret if needed
4. Update `client_secret` in api-keys.json

### "AADSTS700016: Application not found"

**Cause**: Application ID incorrect or app deleted.

**Solution**:
1. Verify `application_id` matches Entra ID exactly
2. Check if app still exists in App registrations

### "Access is denied. Check credentials and try again."

**Cause**: Application access policy restricting access.

**Solution**:
1. Add mailbox to the allowed security group
2. Or remove the application access policy

### "The token contains no permissions, or permissions can not be understood."

**Cause**: API permissions not configured correctly.

**Solution**:
1. Add Mail.Read application permission
2. Grant admin consent
3. Wait a few minutes for propagation

## Security Best Practices

1. **Rotate secrets** before expiration (set calendar reminder)
2. **Use application access policies** to limit mailbox access
3. **Never commit** `api-keys.json` to version control
4. **Monitor audit logs** in Microsoft 365 compliance center
5. **Remove unused permissions** - only request what you need

## Client Secret Expiration

Azure AD client secrets expire. To manage:

1. **Check expiration** in Entra ID → App registrations → Certificates & secrets
2. **Create new secret** before old one expires
3. **Update api-keys.json** with new secret
4. **Delete old secret** after confirming new one works

## API Quotas and Limits

Microsoft Graph has throttling limits:

| Resource | Limit |
|----------|-------|
| Requests per app | 2000/second (per tenant) |
| Messages per request | 1000 max |
| Requests per user | 10000/10 minutes |

For most use cases, you won't hit these limits.

## Permissions Reference

| Permission | Purpose | Type |
|------------|---------|------|
| `Mail.Read` | Read mail in all mailboxes | Application |
| `Mail.ReadBasic` | Read basic mail properties only | Application |
| `User.Read.All` | Read user profile info | Application |
| `MailboxSettings.Read` | Read mailbox settings | Application |

## Configuration Schema

```json
{
  "microsoft_accounts": {
    "<account_name>": {
      "application_id": "GUID - Azure AD app client ID",
      "tenant_id": "GUID - Azure AD tenant ID",
      "client_secret": "Secret value from Certificates & secrets",
      "mailbox": "user@company.com - email to access",
      "_comment": "optional description"
    }
  }
}
```

## Related Files

| File | Purpose |
|------|---------|
| `api-keys.json` | Stores credentials |
| `tools/email/microsoft_auth.py` | Authentication module |
| `tools/email/microsoft/` | Legacy scripts (being deprecated) |

## Migrating from Legacy Settings

If you have existing `tools/email/microsoft/settings.json`:

```bash
# The new system reads from api-keys.json instead
# Copy your credentials:
# - application_id from settings.json → api-keys.json
# - tenant_id from settings.json → api-keys.json
# - secret_value from settings.json → client_secret in api-keys.json
# - Add mailbox email address
```

## Example: Adding Multiple Microsoft Accounts

```json
{
  "microsoft_accounts": {
    "work_main": {
      "application_id": "...",
      "tenant_id": "...",
      "client_secret": "...",
      "mailbox": "me@company.com"
    },
    "work_shared": {
      "application_id": "...",
      "tenant_id": "...",
      "client_secret": "...",
      "mailbox": "shared-inbox@company.com"
    },
    "work_admin": {
      "application_id": "...",
      "tenant_id": "...",
      "client_secret": "...",
      "mailbox": "admin@company.com"
    }
  }
}
```

All accounts can use the same application credentials with different mailbox targets.
