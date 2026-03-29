# WhatsApp Integration Setup

## Overview
The WhatsApp watcher monitors messages for urgent communications. This document explains how to set up WhatsApp monitoring.

## Implementation Options

### Option 1: whatsapp-web.js (Recommended)
Uses Node.js to interface with WhatsApp Web.

**Setup:**
```bash
cd watchers/whatsapp-integration
npm init -y
npm install whatsapp-web.js qrcode-terminal
```

**Create monitor script:**
```javascript
// watchers/whatsapp-integration/monitor.js
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');

const client = new Client({
    authStrategy: new LocalAuth()
});

client.on('qr', (qr) => {
    qrcode.generate(qr, {small: true});
});

client.on('ready', () => {
    console.log('WhatsApp client is ready!');
});

client.on('message', async (message) => {
    const messageData = {
        id: message.id._serialized,
        sender: message.from,
        text: message.body,
        timestamp: new Date().toISOString()
    };

    // Append to messages.json
    const messagesFile = '../whatsapp_session/messages.json';
    let messages = [];
    if (fs.existsSync(messagesFile)) {
        messages = JSON.parse(fs.readFileSync(messagesFile));
    }
    messages.push(messageData);
    fs.writeFileSync(messagesFile, JSON.stringify(messages, null, 2));
});

client.initialize();
```

### Option 2: Playwright Browser Automation
Uses browser automation to monitor WhatsApp Web.

**Setup:**
```bash
pip install playwright
playwright install chromium
```

### Option 3: Manual JSON File (Development)
For testing, manually create messages in `whatsapp_session/messages.json`:

```json
[
  {
    "id": "msg_001",
    "sender": "John Doe",
    "text": "This is urgent! Need help ASAP.",
    "timestamp": "2026-02-24T10:30:00Z"
  }
]
```

## Configuration

Edit `whatsapp_watcher.py` to customize:

```python
# Urgent keywords
self.urgent_keywords = ['urgent', 'asap', 'emergency', 'help', 'critical']

# Important contacts
self.important_contacts = ['Family', 'Boss', 'Client Name']
```

## Running the Watcher

```bash
# Start WhatsApp monitoring (if using Node.js)
cd watchers/whatsapp-integration
node monitor.js

# In another terminal, start the Python watcher
cd watchers
python whatsapp_watcher.py ../vault
```

## Security Notes
- Never commit WhatsApp session files
- Add to .gitignore: `whatsapp_session/`, `.wwebjs_auth/`
- Keep credentials secure
- Use environment variables for sensitive data

## Troubleshooting

**QR Code not appearing:**
- Ensure Node.js is installed
- Check firewall settings
- Try clearing session data

**Messages not detected:**
- Verify messages.json is being updated
- Check file permissions
- Review watcher logs in vault/Logs/
