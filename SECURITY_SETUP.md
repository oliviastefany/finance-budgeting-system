# Security Setup Guide

## Important: Protecting Your API Keys and Credentials

This guide ensures your sensitive data stays secure when pushing to GitHub.

## Initial Setup (Before First Use)

### 1. Create Your Environment File

```bash
# Copy the example file
cp .env.example .env
```

### 2. Edit .env with Your Actual Credentials

Open `.env` and replace the placeholder values:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_finance
DB_USER=your_username
DB_PASSWORD=your_actual_password

EXCHANGE_RATE_API_KEY=your_actual_api_key
```

### 3. Verify .env is Ignored by Git

```bash
# This should show .env in the ignore list
git check-ignore .env

# This should NOT list .env
git status
```

## What's Protected

The `.gitignore` file prevents these sensitive items from being committed:

- `.env` - Your actual API keys and passwords
- `data/` - User transaction data (privacy)
- `models/*.pkl` - Trained models (can be large)
- `logs/` - Log files (may contain sensitive info)
- `*.db`, `*.sqlite` - Database files
- `.venv/` - Virtual environment

## What's Safe to Commit

- `.env.example` - Template with NO real credentials
- Source code in `src/`
- Configuration in `config/config.py` (uses env vars)
- Documentation files
- Requirements and setup files

## Getting API Keys

### Exchange Rate API
1. Visit https://exchangerate.host/ (free tier available)
2. Or use https://openexchangerates.org/
3. Sign up and get your API key
4. Add to `.env` file

## Emergency: If You Accidentally Committed Secrets

If you accidentally committed your `.env` or API keys:

### Option 1: Before Pushing to GitHub
```bash
# Remove the file from git but keep it locally
git rm --cached .env

# Commit the removal
git commit -m "Remove sensitive file"
```

### Option 2: After Pushing to GitHub
1. **Immediately revoke/rotate all exposed API keys**
2. Change all exposed passwords
3. Remove the commit from history:
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

git push origin --force --all
```

4. Consider the repository compromised and create a new one

## Best Practices

1. **Never** hardcode API keys in source code
2. **Always** use environment variables via `os.getenv()`
3. **Double-check** `git status` before committing
4. **Review** changes with `git diff` before committing
5. **Keep** `.env.example` updated when adding new variables
6. **Rotate** API keys periodically
7. **Use** different credentials for development/production

## Verification Checklist

Before pushing to GitHub, verify:

- [ ] `.env` file exists and contains your real credentials
- [ ] `.env` is listed in `.gitignore`
- [ ] `.env.example` exists with placeholder values only
- [ ] `git status` does NOT show `.env` as a change
- [ ] All sensitive data is loaded via environment variables
- [ ] No hardcoded API keys in any `.py` files

## Current Configuration

The project uses environment variables in [config/config.py](config/config.py):

- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Database credentials
- `EXCHANGE_RATE_API_KEY` - Currency conversion API key

All configuration uses `os.getenv()` with safe defaults for non-sensitive values.
