# 🔐 Dashboard Login Credentials

## Access Information

**Dashboard URL:** Your Render deployment URL (e.g., `https://link-tracker.onrender.com`)

### Default Credentials

```
Username: admin_aura_2025
Password: Tr4ck!ng$ecur3#2025
```

## Security Notes

⚠️ **Important Security Recommendations:**

1. **Change Default Password:** It's highly recommended to change the default password after first login
2. **Environment Variables:** Credentials are stored securely in Render environment variables
3. **HTTPS Only:** Always access the dashboard via HTTPS in production
4. **Session Security:** Sessions are protected with Flask's secret key

## Changing Credentials

To change the login credentials:

### Option 1: Via Render Dashboard (Recommended)
1. Go to your Render dashboard
2. Navigate to your `link-tracker` service
3. Go to "Environment" tab
4. Update the values for:
   - `DASHBOARD_USERNAME`
   - `DASHBOARD_PASSWORD`
5. Save changes and redeploy

### Option 2: Via render.yaml
1. Edit `render.yaml` file
2. Update the values in the `envVars` section:
   ```yaml
   - key: DASHBOARD_USERNAME
     value: your_new_username
   - key: DASHBOARD_PASSWORD
     value: your_new_password
   ```
3. Commit and push changes

## Password Requirements

For maximum security, use a password that:
- Is at least 12 characters long
- Contains uppercase and lowercase letters
- Contains numbers
- Contains special characters (!@#$%^&*)
- Is unique (not used elsewhere)

## Session Management

- Sessions are persistent across browser sessions
- Click "LOGOUT" button in the dashboard header to end your session
- Sessions automatically expire when you close your browser (session cookies)

## Troubleshooting

**Can't login?**
- Verify you're using the correct credentials
- Check that environment variables are set in Render
- Clear browser cookies and try again
- Check browser console for errors

**Forgot password?**
- Access Render dashboard to view/reset environment variables
- Or contact your system administrator

---

**Last Updated:** November 2025
**Security Level:** Basic Authentication (recommended for internal use)
