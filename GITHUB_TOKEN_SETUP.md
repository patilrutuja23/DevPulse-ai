# GitHub Token Setup Guide

## Quick Fix for "github_token": false

Your `.env` file currently has an empty `GITHUB_TOKEN`. Follow these steps to fix it:

### Step 1: Get Your GitHub Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `DevPulse AI`
4. Select scopes:
   - ✅ `public_repo` (access public repositories)
   - ✅ `repo` (if you need private repos)
5. Click **"Generate token"**
6. **COPY THE TOKEN** (you won't see it again!)

### Step 2: Add Token to .env

Open your `.env` file and replace:

```
GITHUB_TOKEN=
```

With:

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**IMPORTANT:**
- ❌ NO quotes around the token
- ❌ NO spaces before or after the `=`
- ✅ Just paste the token directly

### Step 3: Restart the Backend

```bash
cd backend
python app.py
```

You should see:
```
============================================================
DevPulse AI - Environment Check
============================================================
ENV TOKEN: ✓ Present
Token Preview: ghp_abc123...
============================================================
```

### Step 4: Verify

Test the health endpoint:
```bash
curl http://127.0.0.1:5000/api/health
```

Should return:
```json
{
  "status": "ok",
  "ibm_bob": false,
  "github_token": true
}
```

## Troubleshooting

### Still showing "github_token": false?

1. **Check .env location**: Must be in the same folder as `app.py`
2. **Check token format**: Should start with `ghp_`
3. **No extra characters**: No quotes, spaces, or newlines
4. **Restart required**: Always restart Flask after changing .env

### Getting 403 errors from GitHub?

- Your token might be expired or invalid
- Generate a new token and update .env
- Make sure you selected the right scopes

### Token working but still rate limited?

- Authenticated requests: 5,000/hour
- Unauthenticated: 60/hour
- Your token is working if you see the higher limit!

## Security Notes

⚠️ **NEVER commit your .env file to Git!**
- It's already in `.gitignore`
- Keep your token secret
- Regenerate if accidentally exposed

✅ **Good practices:**
- Use different tokens for different projects
- Rotate tokens periodically
- Delete unused tokens