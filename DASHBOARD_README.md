# 🕯️ Candle Patterns Dashboard

## Quick Start

### 1. Start the Dashboard

Run this command in your terminal:

```bash
cd "c:\Users\zmgdi\OneDrive\Desktop\CANDLE PATTERNS"
.venv\Scripts\python.exe dashboard_launcher.py
```

The dashboard will:
- Start the server on `http://localhost:8050`
- Automatically open in your default browser
- Be ready for use immediately

### 2. Using the Dashboard

Once the browser opens:

#### Load Sample Data
- Click **"Load sample data"** button in the left sidebar
- The candlestick chart will populate with synthetic BTC data
- Pattern detections will appear in the tabs

#### Upload Your Own CSV
- Click **"Select CSV"** to upload your own market data
- Supported format: CSV with columns `timestamp`, `open`, `high`, `low`, `close`, `volume`
- Data will be automatically validated and stored

#### Explore Patterns
- **Chart tab**: Interactive candlestick chart with detected patterns marked
- **Patterns tab**: List of all detected candle patterns with timestamps
- **Aggregated tab**: Summary of pattern frequencies
- **OPP tab**: Most common sequential patterns

#### Filter & Export
- Use the date range picker to filter data
- Toggle individual pattern types on/off
- Export results as CSV

### 3. Stop the Dashboard

Press `Ctrl+C` in the terminal to stop the server.

---

## Alternative Launchers

If the automatic browser launcher doesn't work:

#### Manual Browser Launch
```bash
.venv\Scripts\python.exe run_simple.py
```
Then manually open http://localhost:8050 in your browser.

#### With Waitress (Production-like Server)
```bash
.venv\Scripts\python.exe start_waitress.py
```
Then open http://localhost:8050 in your browser.

---

## Technical Notes

- **Python Version**: 3.8+
- **Framework**: Dash 3.4.0 + Plotly + Bootstrap
- **Server**: Flask (development) or Waitress (WSGI)
- **Data Storage**: SQLite with persistent artifacts folder
- **Browser Compatibility**: Modern browsers (Chrome, Firefox, Edge, Safari)

---

## Known Issues

On Windows with Python 3.14, the Flask development server requires an actual browser connection to stay stable. The `dashboard_launcher.py` script handles this automatically by opening your browser. If you use `run_simple.py`, you must open the browser manually within ~10 seconds of starting the server.

---

## Support

For issues or questions, check the project logs in:
```
./artifacts/logs/
```
