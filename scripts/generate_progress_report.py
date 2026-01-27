"""Generate a simple weekly progress report from progress_tracker.csv
Usage: python scripts/generate_progress_report.py
"""
import csv
from collections import defaultdict

TRACKER = "progress_tracker.csv"

if __name__ == "__main__":
    summary = defaultdict(int)
    rows = []
    with open(TRACKER, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
            summary[row['status']] += 1

    print("Weekly Progress Report")
    print("======================")
    print(f"Total tasks: {len(rows)}")
    for status, count in summary.items():
        print(f" - {status}: {count}")
    print('\nTop tasks:')
    for row in rows:
        print(f"{row['id']}: {row['title']} [{row['status']}] {row['pct_complete']}%")
