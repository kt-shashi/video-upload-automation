# Fix Google OAuth "Access Blocked" Error

## Problem
You're seeing: "Valorant Automation has not completed the Google verification process"

This happens because your OAuth app is in "Testing" mode and your email isn't added as a test user.

## Solution: Add Yourself as a Test User

### Step 1: Go to Google Cloud Console
1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (the one you created for YouTube API)

### Step 2: Navigate to OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**
2. You should see your app in "Testing" mode

### Step 3: Add Test Users
1. Scroll down to the **"Test users"** section
2. Click **"+ ADD USERS"**
3. Add your Google account email address (the one you use to sign in)
4. Click **"ADD"**

### Step 4: Try Again
1. Run your upload script again
2. When prompted to sign in, use the email you just added
3. You should now be able to authenticate successfully

## Alternative: Publish Your App (Not Recommended for Personal Use)

If you want to make it available to anyone (not just test users):
1. Go to **OAuth consent screen**
2. Click **"PUBLISH APP"**
3. **Warning**: This requires Google verification for sensitive scopes (like YouTube upload)
4. For personal use, adding test users is easier and faster

## Quick Checklist

- [ ] Go to Google Cloud Console
- [ ] Navigate to OAuth consent screen
- [ ] Add your email as a test user
- [ ] Try running the script again
- [ ] Sign in with the test user email

## Still Having Issues?

If you're still blocked after adding yourself as a test user:
1. Make sure you're signing in with the exact email you added
2. Wait a few minutes for changes to propagate
3. Clear your browser cache and try again
4. Check that you're using the correct Google account

