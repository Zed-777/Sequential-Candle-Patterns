# Candle Patterns — User Manual

**Simple Instructions for Using the Application**

---

## What Is This?

Candle Patterns is a tool that analyzes candlestick charts from financial markets (stocks, crypto, forex, etc.). It finds patterns in how candles change color and predicts what might happen next.

**You don't need to be a programmer to use it.** Just follow these simple steps.

---

## Getting Started

### Step 1: Open the Application

**On Windows:**

1. Open your Terminal or Command Prompt
2. Copy and paste this command:

```
docker run -p 8050:8050 candle-patterns:latest run
```

1. Wait 10 seconds
2. Your web browser will automatically open to the application

**No Docker?** Ask your administrator to help, or follow the local setup guide at the end.

### Step 2: You'll See the Dashboard

The app opens in your web browser. It looks like a chart with controls on the left side.

---

## Using the Dashboard

### Load Sample Data

**To quickly see how it works:**

1. Look on the **left side** of the screen
2. Click the button that says **"Load sample data"**
3. Wait 2 seconds
4. A chart will appear with candlesticks (colored red 🔴 and green 🟢)
5. Pattern detections will automatically appear

### Upload Your Own Data

**To analyze your own market data:**

1. On the left side, click **"Select CSV"** button
2. Select a file from your computer with this information:
   - `timestamp` — date and time of the candle
   - `open` — opening price
   - `high` — highest price
   - `low` — lowest price
   - `close` — closing price
   - `volume` — trading volume

3. Click **"Upload"**
4. Your data will load and patterns will be detected

### Explore the Tabs

The dashboard has different tabs (sections). Click on them to see different views:

| Tab | What You See |
|-----|-------------|
| **Chart** | Candlestick chart with detected patterns marked |
| **Patterns** | List of all patterns found with dates |
| **Aggregated** | Summary showing which patterns appear most often |
| **OPP** | Most common sequences (what comes after what) |
| **Statistics** | Win rates and returns for each pattern |
| **Backtest** | How patterns would have performed in the past |

### Filter Your Data

**See only the data you care about:**

1. Find the **date picker** on the left side
2. Click and select a start date and end date
3. The chart updates automatically
4. Use checkboxes to toggle patterns on/off

### Export Your Results

**Save your findings:**

1. Look for the **"Export"** button
2. Results download as a CSV file to your computer
3. Open in Excel or Google Sheets if needed

---

## Stopping the Application

**When you're done:**

1. Go back to your Terminal/Command Prompt where you started it
2. Press and hold `Ctrl` then press `C`
3. Type `Y` and press Enter
4. The application stops

---

## Troubleshooting

### The App Doesn't Open

- Make sure Docker is installed on your computer
- Wait 10-15 seconds before opening your browser manually
- Go to: `http://localhost:8050`

### The Chart Doesn't Show Data

- Make sure you clicked "Load sample data" or uploaded a CSV
- Check that your CSV file has the right columns

### It's Running Slow

- Close other browser tabs
- Refresh the page (press F5)
- Don't upload files larger than 100 MB

### I See an Error

- Check that you're using a modern web browser (Chrome, Firefox, Edge, Safari)
- Try clearing your browser cache

---

## Common Questions

### Can I use this offline?

Not easily. The app needs the Docker container running. Once started, you can use it without internet.

### What file format do I need?

CSV (comma-separated values). Open it in Excel to check the format.

### Can I share my results?

Yes! Use the "Export" button to save as CSV. You can email the file to others.

### Is my data private?

Your data stays on your machine. We don't upload anything to the cloud.

---

## Getting Help

**Not sure what to do?**

1. Check the **CONTRIBUTING.md** file for more detailed technical help
2. Contact the maintainer: [@Zed-777](https://github.com/Zed-777)
3. Open an issue on GitHub

---

## Local Setup (If Docker Doesn't Work)

If Docker isn't available, here's how to run it locally:

### Windows PowerShell

```powershell
# 1. Clone the code
git clone https://github.com/Zed-777/candle-patterns.git
cd candle-patterns

# 2. Set up environment
.\scripts\setup_venv.ps1
.\.venv\Scripts\Activate.ps1

# 3. Install
pip install -e .

# 4. Run the dashboard
python -m candle_patterns.dashboard
```

### Mac/Linux

```bash
# 1. Clone the code
git clone https://github.com/Zed-777/candle-patterns.git
cd candle-patterns

# 2. Set up environment
bash scripts/setup_venv.sh
source .venv/bin/activate

# 3. Install
pip install -e .

# 4. Run the dashboard
python -m candle_patterns.dashboard
```

Then go to: `http://localhost:8050`

---

**Last Updated:** April 2, 2026  
**For Developers:** See PROJECT_GUIDELINES.md and CONTRIBUTING.md
