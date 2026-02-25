from __future__ import annotations


import re

import pandas as pd

from typing import List, Tuple

# Import detection helpers lazily inside functions to avoid circular imports


PatternToken = Tuple[int, str]  # (count, token) token e.g. 'R','G','Doji'


def parse_sequence(seq: str) -> List[PatternToken]:
    """Parse a sequence string like '3R -> 2G' or '5G ÔåÆ Doji ÔåÆ 4R' into tokens."""

    # split on arrow-like separators (ÔåÆ, ->, -, >)

    parts = re.split(r"\s*(?:ÔåÆ|->|>|-)\s*", seq)

    tokens: List[PatternToken] = []

    for p in parts:

        p = p.strip()

        m = re.match(r"^(\d+)([RG])$", p, re.IGNORECASE)

        if m:

            cnt = int(m.group(1))

            sym = m.group(2).upper()

            tokens.append((cnt, sym))

        else:

            # named token like Doji or Hammer; treat as count=1

            tokens.append((1, p))

    return tokens


def symbol_sequence(df: pd.DataFrame) -> List[str]:
    """Return simple symbol per candle: 'G' or 'R' or 'Doji' if detected."""

    syms: List[str] = []

    # import helpers here to avoid circular imports

    from .detection import is_doji, candle_color

    for i in range(len(df)):

        row = df.iloc[i]

        if is_doji(df.iloc[i : i + 1]):

            syms.append("Doji")

            continue

        c = candle_color(row)

        syms.append("G" if c == "green" else "R")

    return syms


def match_named_token(df: pd.DataFrame, idx: int, token: str) -> bool:
    """Check if token matches candle at idx. Token may be 'Doji','Hammer', etc."""

    # import helpers here to avoid circular imports

    from .detection import is_doji, is_hammer

    token_low = token.lower()

    # named tokens used for pattern matching (not passwords) - B105 false positive
    if token_low == "doji":  # nosec B105

        return bool(is_doji(df.iloc[idx : idx + 1]))

    if token_low == "hammer":  # nosec B105

        return bool(is_hammer(df.iloc[idx : idx + 1]))

    # fallback to direction tokens handled elsewhere

    return False


def find_sequence_occurrences(df: pd.DataFrame, seq_str: str) -> List[int]:
    """Find all ending indices where the given sequence occurs. Returns list of end indices."""

    tokens = parse_sequence(seq_str)

    syms = symbol_sequence(df)

    results: List[int] = []

    n = len(df)

    for start in range(0, n):

        i = start

        ok = True

        for cnt, tok in tokens:

            # if token is direction 'R'/'G'

            if tok in ("R", "G"):

                # need cnt consecutive tokens of tok starting at i

                for k in range(cnt):

                    if i + k >= n or syms[i + k] != tok:

                        ok = False

                        break

                if not ok:

                    break

                i += cnt

            else:

                # named tokens: must match single candle

                if i >= n or not match_named_token(df, i, tok):

                    ok = False

                    break

                i += 1

        if ok:

            results.append(i - 1)  # end index

    return results


# ============================================================================
# WILDCARD SEQUENCE MATCHING  —  "3R -> * -> 2G"
# ============================================================================

def find_wildcard_sequence(
    df: pd.DataFrame,
    seq_str: str,
    wildcard_min: int = 1,
    wildcard_max: int = 3,
) -> List[dict]:
    """Match a sequence containing ``*`` wildcards that span 1-N candles.

    A ``*`` in the sequence matches *any* ``wildcard_min`` to ``wildcard_max``
    candles regardless of colour/type.

    Returns a list of dicts::

        [{"start_idx": 2, "end_idx": 9, "wildcard_span": 2}, ...]
    """
    parts = re.split(r"\s*(?:→|->|>|-)\s*", seq_str)

    # Split into segments separated by wildcards
    segments: List = []  # Each is either ("tokens", [...]) or ("wild",)
    for p in parts:
        p = p.strip()
        if p == "*":
            segments.append(("wild",))
        else:
            m = re.match(r"^(\d+)([RG])$", p, re.IGNORECASE)
            if m:
                segments.append(("tokens", [(int(m.group(1)), m.group(2).upper())]))
            else:
                segments.append(("tokens", [(1, p)]))

    syms = symbol_sequence(df)
    n = len(syms)
    results: List[dict] = []

    def _match_from(pos: int, seg_idx: int) -> List[dict]:
        """Recursive matcher that yields list of match dicts."""
        if seg_idx >= len(segments):
            return [{"end": pos - 1, "wild_span": 0}]
        seg = segments[seg_idx]
        if seg[0] == "wild":
            hits: List[dict] = []
            for span in range(wildcard_min, wildcard_max + 1):
                if pos + span > n:
                    break
                sub = _match_from(pos + span, seg_idx + 1)
                for h in sub:
                    hits.append({"end": h["end"], "wild_span": h["wild_span"] + span})
            return hits
        else:
            # token segment — must match exactly
            i = pos
            for cnt, tok in seg[1]:
                if tok in ("R", "G"):
                    for k in range(cnt):
                        if i + k >= n or syms[i + k] != tok:
                            return []
                    i += cnt
                else:
                    if i >= n or not match_named_token(df, i, tok):
                        return []
                    i += 1
            return _match_from(i, seg_idx + 1)

    for start in range(n):
        hits = _match_from(start, 0)
        for h in hits:
            results.append({
                "start_idx": start,
                "end_idx": h["end"],
                "wildcard_span": h["wild_span"],
            })

    return results


# ============================================================================
# WHAT-COMES-NEXT PREDICTION
# ============================================================================

def what_comes_next(
    df: pd.DataFrame,
    seq_str: str,
    lookahead: int = 3,
) -> dict:
    """After every occurrence of *seq_str*, collect the next *lookahead* candle
    colours and tally the distribution.

    Returns::

        {
            "total_occurrences": 8,
            "lookahead": 3,
            "distribution": [
                {"position": 1, "R": 5, "G": 2, "Doji": 1, "R_pct": 0.625, "G_pct": 0.25, "Doji_pct": 0.125},
                ...
            ],
            "most_likely_next": "3R"   # run-length encoded most-common continuation
        }
    """
    ends = find_sequence_occurrences(df, seq_str)
    syms = symbol_sequence(df)
    n = len(syms)

    dist: List[dict] = []
    continuations: List[tuple] = []

    for pos in range(lookahead):
        counter: dict = {"R": 0, "G": 0, "Doji": 0}
        for end_idx in ends:
            nxt = end_idx + 1 + pos
            if nxt < n:
                s = syms[nxt]
                counter[s] = counter.get(s, 0) + 1
        total = sum(counter.values())
        entry = {"position": pos + 1}
        for k in ("R", "G", "Doji"):
            entry[k] = counter.get(k, 0)
            entry[f"{k}_pct"] = round(counter.get(k, 0) / max(1, total), 4)
        dist.append(entry)

    # Build most-likely continuation string
    likely: List[str] = []
    for d in dist:
        best = max(("R", "G", "Doji"), key=lambda k: d.get(k, 0))
        if d.get(best, 0) > 0:
            likely.append(best)
    most_likely = _run_length_encode(tuple(likely)) if likely else ""

    return {
        "total_occurrences": len(ends),
        "lookahead": lookahead,
        "distribution": dist,
        "most_likely_next": most_likely,
    }


# ============================================================================
# SEQUENCE OUTCOME STATISTICS  —  price movement after matches
# ============================================================================

def sequence_outcome_stats(
    df: pd.DataFrame,
    seq_str: str,
    hold_candles: int = 5,
) -> dict:
    """Compute price statistics for *hold_candles* after each occurrence of seq_str.

    Returns::

        {
            "sequence": "3R -> 2G",
            "occurrences": 6,
            "avg_return_pct": 0.45,
            "median_return_pct": 0.32,
            "win_rate": 0.667,
            "max_gain_pct": 2.1,
            "max_loss_pct": -1.3,
            "avg_high_pct": 1.2,
            "avg_low_pct": -0.8,
        }
    """
    ends = find_sequence_occurrences(df, seq_str)
    n = len(df)

    returns: List[float] = []
    highs: List[float] = []
    lows: List[float] = []

    for end_idx in ends:
        entry_idx = end_idx + 1
        if entry_idx >= n:
            continue
        entry_close = float(df.iloc[entry_idx]["close"])
        exit_idx = min(entry_idx + hold_candles, n - 1)
        if exit_idx <= entry_idx:
            continue

        # Hold period metrics
        window = df.iloc[entry_idx : exit_idx + 1]
        exit_close = float(window.iloc[-1]["close"])
        ret_pct = (exit_close - entry_close) / entry_close * 100

        max_high = float(window["high"].max())
        min_low = float(window["low"].min())
        high_pct = (max_high - entry_close) / entry_close * 100
        low_pct = (min_low - entry_close) / entry_close * 100

        returns.append(round(ret_pct, 4))
        highs.append(round(high_pct, 4))
        lows.append(round(low_pct, 4))

    if not returns:
        return {
            "sequence": seq_str,
            "occurrences": len(ends),
            "avg_return_pct": 0,
            "median_return_pct": 0,
            "win_rate": 0,
            "max_gain_pct": 0,
            "max_loss_pct": 0,
            "avg_high_pct": 0,
            "avg_low_pct": 0,
        }

    sorted_rets = sorted(returns)
    mid = len(sorted_rets) // 2
    median = sorted_rets[mid] if len(sorted_rets) % 2 else (sorted_rets[mid - 1] + sorted_rets[mid]) / 2

    wins = sum(1 for r in returns if r > 0)

    return {
        "sequence": seq_str,
        "occurrences": len(ends),
        "avg_return_pct": round(sum(returns) / len(returns), 4),
        "median_return_pct": round(median, 4),
        "win_rate": round(wins / len(returns), 4),
        "max_gain_pct": round(max(returns), 4),
        "max_loss_pct": round(min(returns), 4),
        "avg_high_pct": round(sum(highs) / len(highs), 4),
        "avg_low_pct": round(sum(lows) / len(lows), 4),
    }


def sequence_length(seq_str: str) -> int:
    """Return the total number of candles consumed by a sequence string."""
    tokens = parse_sequence(seq_str)
    return sum(cnt for cnt, _ in tokens)


def _run_length_encode(syms: tuple) -> str:
    """Convert ('R','R','R','G','G') to '3R -> 2G'."""
    if not syms:
        return ""
    parts: List[str] = []
    current = syms[0]
    count = 1
    for s in syms[1:]:
        if s == current:
            count += 1
        else:
            parts.append(f"{count}{current}" if current in ("R", "G") else current)
            current = s
            count = 1
    parts.append(f"{count}{current}" if current in ("R", "G") else current)
    return " -> ".join(parts)


def discover_color_sequences(
    df: pd.DataFrame,
    min_len: int = 3,
    max_len: int = 8,
    top_k: int = 20,
) -> List[dict]:
    """Auto-discover the most common R/G colour sequences in *df*.

    Returns a list of dicts sorted by count descending::

        [{"sequence": "3R -> 2G", "count": 12, "length": 5, "support": 0.061}, ...]
    """
    from .detection import is_doji, candle_color  # local import to avoid circular

    syms = symbol_sequence(df)
    n = len(syms)

    # Count raw sub-sequences of each window length
    raw_counts: dict = {}
    for length in range(min_len, max_len + 1):
        for start in range(n - length + 1):
            window = tuple(syms[start : start + length])
            raw_counts[window] = raw_counts.get(window, 0) + 1

    # Merge into run-length-encoded strings
    encoded_counts: dict = {}
    for seq_tuple, count in raw_counts.items():
        encoded = _run_length_encode(seq_tuple)
        encoded_counts[encoded] = encoded_counts.get(encoded, 0) + count

    # Sort by count desc
    sorted_seqs = sorted(encoded_counts.items(), key=lambda x: x[1], reverse=True)

    results: List[dict] = []
    for seq_str, count in sorted_seqs[:top_k]:
        length = sequence_length(seq_str)
        support = count / max(1, n - length + 1)
        results.append(
            {
                "sequence": seq_str,
                "count": count,
                "length": length,
                "support": round(support, 4),
            }
        )

    return results
