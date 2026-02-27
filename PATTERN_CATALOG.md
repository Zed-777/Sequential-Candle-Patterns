# Example Sequential Patterns the System Must Detect

The system must be capable of identifying **any type of sequential pattern** in candlestick data, including but not limited to the examples below. Patterns may involve candle direction, size, wicks, volatility, or multiÔÇæfactor combinations.

---

## **1. Basic Candle-Sequence Patterns**

- `9R ÔåÆ 2G`  
- `3R ÔåÆ 3G ÔåÆ 3R ÔåÆ 5G`  
- `5G ÔåÆ 1R ÔåÆ 4G`  
- `2R ÔåÆ 1G ÔåÆ 2R ÔåÆ 1G ÔåÆ 4R`  

---

## **2. Trend-Continuation Patterns**

- `HH + HL ├ù 3 ÔåÆ Bullish continuation`  
- `LH + LL ├ù 2 ÔåÆ Bearish continuation`  
- `3G with increasing body size ÔåÆ 2ÔÇô4 more G`  
- `4R with shrinking wicks ÔåÆ exhaustion ÔåÆ reversal`  

---

## **3. Reversal Patterns (Sequence-Based)**

- `7R with decreasing body size ÔåÆ 3G reversal`  
- `5G ÔåÆ Doji ÔåÆ 4R`  
- `Long lower wick ÔåÆ 2R ÔåÆ 4G`  
- `3R ÔåÆ Hammer ÔåÆ 3G`  

---

## **4. Volatility-Driven Patterns**

- `3 small candles ÔåÆ 1 large breakout candle`  
- `5-candle low-volatility cluster ÔåÆ volatility expansion`  
- `Alternating large/small candles ÔåÆ trend instability`  

---

## **5. AI-Discoverable Hidden Patterns**

- `R R G G R G G G R ÔåÆ G G`  
- `Small G ÔåÆ Large R ÔåÆ Small R ÔåÆ Large G ÔåÆ G ÔåÆ G`  
- `Wick-dominant ÔåÆ 2R ÔåÆ 1G ÔåÆ Wick-dominant ÔåÆ 4G`  

---

## **6. Statistical / Probabilistic Patterns**

- `4R ÔåÆ next candle is G (61% probability)`  
- `2G ÔåÆ 2R repeats 14% of the time`  
- `3R ÔåÆ 1G ÔåÆ 2G continuation (48% probability)`  
- `5 small candles ÔåÆ breakout within 3 candles (72% probability)`  

---

## **7. Multi-Factor Patterns**

- `3R + rising volume ÔåÆ 2G with long lower wicks ÔåÆ bullish reversal`  
- `Inside bar ÔåÆ Inside bar ÔåÆ Breakout ÔåÆ 4G continuation`  
- `Large G ÔåÆ Small G ÔåÆ Doji ÔåÆ Large G`  
- `Long upper wick ÔåÆ 2R ÔåÆ 1G ÔåÆ 3R`  

---

## **8. Meta-Patterns (Patterns of Patterns)**

- `3R ÔåÆ 2G repeating twice within 20 candles ÔåÆ 5G rally (54% probability)`  
- `Nested pattern: 2G micro-pattern inside 5R macro-pattern ÔåÆ reversal`  
- `Fractal repetition: 2R ÔåÆ 1G repeated 3├ù ÔåÆ large bullish move`  

---

## **System Requirements Based on These Examples**

The system must:

- Detect **variable-length** sequences
- Detect **multi-factor** sequences (direction, size, wicks, volatility, volume)
- Detect **probabilistic** patterns with confidence/support metrics
- Detect **rare or hidden** patterns using AI/ML
- Detect **meta-patterns**, including repetition and fractal structures
- Work on any CSV containing OHLC data

---

## Recent additions (automated update)

- **Rule-based detectors added:** Spinning Top, Shooting Star, Hanging Man, Piercing Line, Morning Star, Evening Star.
- **Notes:** These detectors use simple, conservative heuristics suitable for synthetic unit tests; further parameterization will be added as part of ML calibration and validation.

---

## Phase 2 Pattern Expansion (February 22, 2026)

### New Patterns Added (5)

| Pattern | Type | Description | Detection Logic |
|---------|------|-------------|-----------------|
| **Dark Cloud Cover** | Bearish Reversal | Green candle followed by red candle that opens above prior close and closes below midpoint of prior body | 2-candle pattern: prior green, current red opens above prior close, closes below (prior open + prior close) / 2 |
| **Bullish Harami** | Bullish Reversal | Small green candle contained entirely within prior large red candle's range | 2-candle pattern: prior red, current green with high < prior high AND low > prior low |
| **Bearish Harami** | Bearish Reversal | Small red candle contained entirely within prior large green candle's range | 2-candle pattern: prior green, current red with high < prior high AND low > prior low |
| **On Neck Line** | Bearish Continuation | After a red candle, a second red candle closes at or very near the prior candle's low | 2-candle pattern: both red, current close ≈ prior low (tolerance: 1% of prior high) |
| **In Neck Line** | Bearish Continuation | After a red candle, a second red candle closes above the prior close but opens below the prior open | 2-candle pattern: both red, current close > prior close, current open < prior open |

### Complete Pattern Catalog (17 patterns)

| # | Pattern | Type | Candles Required |
|---|---------|------|------------------|
| 1 | Doji | Neutral/Reversal | 1 |
| 2 | Hammer | Bullish Reversal | 1 |
| 3 | Spinning Top | Neutral | 1 |
| 4 | Shooting Star | Bearish Reversal | 1 |
| 5 | Hanging Man | Bearish Reversal | 1 |
| 6 | Bullish Engulfing | Bullish Reversal | 2 |
| 7 | Bearish Engulfing | Bearish Reversal | 2 |
| 8 | Piercing Line | Bullish Reversal | 2 |
| 9 | Dark Cloud Cover | Bearish Reversal | 2 |
| 10 | Bullish Harami | Bullish Reversal | 2 |
| 11 | Bearish Harami | Bearish Reversal | 2 |
| 12 | On Neck Line | Bearish Continuation | 2 |
| 13 | In Neck Line | Bearish Continuation | 2 |
| 14 | Three White Soldiers | Bullish Continuation | 3 |
| 15 | Three Black Crows | Bearish Continuation | 3 |
| 16 | Morning Star | Bullish Reversal | 3 |
| 17 | Evening Star | Bearish Reversal | 3 |

### Test Coverage

- 10 dedicated unit tests for new patterns (positive + negative cases)
- Integration test verifying all patterns registered in RULES
- Total test suite: **48 passed, 2 skipped**
