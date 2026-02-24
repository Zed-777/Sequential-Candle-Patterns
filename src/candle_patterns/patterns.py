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
