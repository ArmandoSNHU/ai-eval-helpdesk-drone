"""
Offline, zero-dependency analysis script for AI helpdesk & drone evaluations.

Usage:
    From the project root, run:

        python3 src/evaluate_responses.py

This version does NOT require pandas or any external packages.
It only uses the Python standard library, which makes it suitable
for locked-down environments (like work machines or WSL without internet).
"""

from pathlib import Path
import csv
from collections import defaultdict
from statistics import mean


RATINGS_FILE = Path(__file__).resolve().parents[1] / "data" / "model_ratings_v1.csv"


def load_ratings(path: Path):
    """Load ratings from a CSV file into a list of dicts."""
    if not path.exists():
        print(f"[!] Ratings file not found: {path}")
        print("    Make sure data/model_ratings_v1.csv exists and has at least a header row.")
        return []

    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip completely empty rows
            if not any(row.values()):
                continue

            # Convert numeric fields safely
            for field in ["tech_accuracy", "clarity", "policy_safety", "tone", "total_score"]:
                if field in row and row[field].strip():
                    try:
                        row[field] = float(row[field])
                    except ValueError:
                        # If it's not a number, set to None and ignore in averages
                        row[field] = None
                else:
                    row[field] = None

            rows.append(row)

    return rows


def summarize_by_model(ratings):
    """
    Group ratings by (model_version, domain) and compute averages.
    Returns a list of summary dicts.
    """
    groups = defaultdict(list)

    for row in ratings:
        model_version = row.get("model_version", "unknown")
        domain = row.get("domain", "unknown")
        key = (model_version, domain)
        groups[key].append(row)

    summaries = []

    for (model_version, domain), rows in groups.items():
        def safe_avg(field):
            vals = [r[field] for r in rows if isinstance(r[field], (int, float))]
            return mean(vals) if vals else None

        summary = {
            "model_version": model_version,
            "domain": domain,
            "tech_accuracy_avg": safe_avg("tech_accuracy"),
            "clarity_avg": safe_avg("clarity"),
            "policy_safety_avg": safe_avg("policy_safety"),
            "tone_avg": safe_avg("tone"),
            "total_avg": safe_avg("total_score"),
            "samples": len(rows),
        }
        summaries.append(summary)

    return summaries


def format_float(value, width=6, digits=2):
    """Format a float nicely for table output."""
    if value is None:
        return " " * width
    return f"{value:{width}.{digits}f}"


def print_summary_table(summaries):
    if not summaries:
        print("\n[!] No ratings available to summarize.")
        print("    Add some rows to data/model_ratings_v1.csv and re-run.\n")
        return

    # Table header
    print("\n=== Model Evaluation Summary (No External Dependencies) ===\n")
    header = (
        f"{'Model':12} {'Domain':10} "
        f"{'Tech':>6} {'Clar':>6} {'Policy':>6} {'Tone':>6} {'Total':>6} {'N':>4}"
    )
    print(header)
    print("-" * len(header))

    # Rows
    for s in summaries:
        line = (
            f"{s['model_version'][:12]:12} "
            f"{s['domain'][:10]:10} "
            f"{format_float(s['tech_accuracy_avg'])} "
            f"{format_float(s['clarity_avg'])} "
            f"{format_float(s['policy_safety_avg'])} "
            f"{format_float(s['tone_avg'])} "
            f"{format_float(s['total_avg'])} "
            f"{s['samples']:4d}"
        )
        print(line)

    print("\nQuick reading guide:")
    print("- Higher 'Total' = better overall model behavior.")
    print("- Compare domains to see where the model is stronger (helpdesk vs drone).\n")


def main():
    print(f"Using ratings file: {RATINGS_FILE}")
    ratings = load_ratings(RATINGS_FILE)
    summaries = summarize_by_model(ratings)
    print_summary_table(summaries)


if __name__ == "__main__":
    main()
