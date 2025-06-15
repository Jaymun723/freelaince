# How to Load Freelaince Extension in Chrome

## Quick Setup

1. **Start the Server**:
   ```bash
   npm run start
   # or: cd server && python3 server.py
   ```

2. **Load Extension in Chrome**:
   - Open `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select this folder: `/home/caro_/code/freelaince/front`

3. **Test the Extension**:
   - Open any webpage
   - Look for the Freelaince button (🚀 icon) in bottom right
   - Click it and start chatting!

## What Gets Loaded

The `.chromeignore` file excludes:
- ✅ `server/` directory (Python files, cache, logs)
- ✅ `node_modules/`
- ✅ `__pycache__/`
- ✅ Development files (`.py`, `package.json`, etc.)

Only the extension files are loaded:
- `manifest.json`
- `background.js`
- `content.js`
- `popup.html/js`
- `styles.css`
- `icon*.png`

## Troubleshooting

**Extension not showing up?**
- Check Chrome Developer mode is enabled
- Reload the extension if you made changes

**Can't connect to server?**
- Make sure server is running (`npm start`)
- Check WebSocket URL in extension popup (should be `ws://localhost:8080`)

**Server not responding?**
- Install dependencies: `npm run install-deps`
- Check server logs for errors