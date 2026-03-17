# Authentication Guide

Lemlist uses HTTP Basic Authentication with an empty username and your API key as the password.

## Getting Your API Key

1. Log in to your Lemlist account
2. Go to **Settings** → **Integrations**
3. Copy your API key

## Authentication Methods

### Method 1: curl --user (Recommended)

```bash
curl --user ":$LEMLIST_API_KEY" \
  "https://api.lemlist.com/api/campaigns"
```

**Important:** Note the colon (`:`) before `$LEMLIST_API_KEY`. The username is empty.

### Method 2: Authorization Header

```bash
# Base64 encode ":API_KEY"
AUTH=$(echo -n ":$LEMLIST_API_KEY" | base64)

curl -H "Authorization: Basic $AUTH" \
  "https://api.lemlist.com/api/campaigns"
```

### Method 3: Query Parameter

```bash
curl "https://api.lemlist.com/api/campaigns?access_token=$LEMLIST_API_KEY"
```

## Setting Environment Variable

### Linux/macOS

```bash
export LEMLIST_API_KEY="your_api_key_here"
```

Add to `~/.bashrc` or `~/.zshrc` for persistence:

```bash
echo 'export LEMLIST_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### Windows (PowerShell)

```powershell
$env:LEMLIST_API_KEY="your_api_key_here"
```

### Windows (CMD)

```cmd
set LEMLIST_API_KEY=your_api_key_here
```

## Testing Authentication

```bash
# Should return your team info
curl -s --user ":$LEMLIST_API_KEY" \
  "https://api.lemlist.com/api/team" | jq .
```

Expected response:
```json
{
  "_id": "tea_xxx",
  "name": "Your Team Name",
  "users": [...],
  "mailboxes": [...]
}
```

## Troubleshooting

### "The authentication you supplied is incorrect"

**Cause:** Invalid or missing API key

**Solutions:**
1. Check that `LEMLIST_API_KEY` is set:
   ```bash
   echo $LEMLIST_API_KEY
   ```
2. Verify the API key is correct in Lemlist settings
3. Ensure you're using the colon prefix: `:API_KEY`

### "No API key provided"

**Cause:** Header not properly formatted

**Solution:** Use `--user ":$LEMLIST_API_KEY"` format

### "User linked to this API key is blocked"

**Cause:** Account restrictions

**Solution:** Contact Lemlist support

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Use .env files** - For local development
3. **Rotate keys regularly** - Generate new keys periodically
4. **Limit access** - Use minimal required permissions
5. **Monitor usage** - Check for unauthorized access

## Python Example

```python
import os
import requests
from requests.auth import HTTPBasicAuth

api_key = os.getenv("LEMLIST_API_KEY")
auth = HTTPBasicAuth("", api_key)  # Empty username

response = requests.get(
    "https://api.lemlist.com/api/campaigns",
    auth=auth
)
print(response.json())
```

## Node.js Example

```javascript
const axios = require('axios');

const apiKey = process.env.LEMLIST_API_KEY;
const auth = Buffer.from(`:${apiKey}`).toString('base64');

axios.get('https://api.lemlist.com/api/campaigns', {
  headers: {
    'Authorization': `Basic ${auth}`
  }
}).then(response => {
  console.log(response.data);
});
```
