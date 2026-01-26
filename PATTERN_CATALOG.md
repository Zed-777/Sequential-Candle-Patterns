## **Example Sequential Patterns the System Must Detect**

The system must be capable of identifying **any type of sequential pattern** in candlestick data, including but not limited to the examples below. Patterns may involve candle direction, size, wicks, volatility, or multi‑factor combinations.

---

## **1. Basic Candle-Sequence Patterns**
- `9R → 2G`  
- `3R → 3G → 3R → 5G`  
- `5G → 1R → 4G`  
- `2R → 1G → 2R → 1G → 4R`  

---

## **2. Trend-Continuation Patterns**
- `HH + HL × 3 → Bullish continuation`  
- `LH + LL × 2 → Bearish continuation`  
- `3G with increasing body size → 2–4 more G`  
- `4R with shrinking wicks → exhaustion → reversal`  

---

## **3. Reversal Patterns (Sequence-Based)**
- `7R with decreasing body size → 3G reversal`  
- `5G → Doji → 4R`  
- `Long lower wick → 2R → 4G`  
- `3R → Hammer → 3G`  

---

## **4. Volatility-Driven Patterns**
- `3 small candles → 1 large breakout candle`  
- `5-candle low-volatility cluster → volatility expansion`  
- `Alternating large/small candles → trend instability`  

---

## **5. AI-Discoverable Hidden Patterns**
- `R R G G R G G G R → G G`  
- `Small G → Large R → Small R → Large G → G → G`  
- `Wick-dominant → 2R → 1G → Wick-dominant → 4G`  

---

## **6. Statistical / Probabilistic Patterns**
- `4R → next candle is G (61% probability)`  
- `2G → 2R repeats 14% of the time`  
- `3R → 1G → 2G continuation (48% probability)`  
- `5 small candles → breakout within 3 candles (72% probability)`  

---

## **7. Multi-Factor Patterns**
- `3R + rising volume → 2G with long lower wicks → bullish reversal`  
- `Inside bar → Inside bar → Breakout → 4G continuation`  
- `Large G → Small G → Doji → Large G`  
- `Long upper wick → 2R → 1G → 3R`  

---

## **8. Meta-Patterns (Patterns of Patterns)**
- `3R → 2G repeating twice within 20 candles → 5G rally (54% probability)`  
- `Nested pattern: 2G micro-pattern inside 5R macro-pattern → reversal`  
- `Fractal repetition: 2R → 1G repeated 3× → large bullish move`  

---

## **System Requirements Based on These Examples**
The system must:

- Detect **variable-length** sequences
- Detect **multi-factor** sequences (direction, size, wicks, volatility, volume)
- Detect **probabilistic** patterns with confidence/support metrics
- Detect **rare or hidden** patterns using AI/ML
- Detect **meta-patterns**, including repetition and fractal structures
- Work on any CSV containing OHLC data
