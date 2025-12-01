"""
add_rating.py
-------------
Offline, zero-dependency helper to append new evaluation rows to:
    data/model_ratings_v1.csv

Usage:
    python3 src/add_rating.py
"""

from pathlib import Path
import csv
import datetime

# Path to the ratings file
RATINGS_FILE = Path(__file__).resolve().parents[1] / "data" / "model_ratings_v1.csv"


def prompt_float(field_name):
    while True:
        value = input(f"{field_name} (1–5): ").strip()
        if value == "":
            print("Please enter a number from 1 to 5.")
            continue
        try:
            value = float(value)
            if 1 <= value <= 5:
                return value
            else:
                print("Must be between 1 and 5.")
        except ValueError:
            print("Not a valid number. Try again.")


def add_rating():
    print("\n=== Add New AI Rating ===\n")

    # Collect info interactively
    id_val = input("ID (ex: H009 or D010): ").strip()
    domain = input("Domain (helpdesk/drone): ").strip().lower()
    model_version = input("Model Version (ex: gpt-v1): ").strip()

    print("\nEnter scores (1–5):")
    tech_accuracy = prompt_float("Technical Accuracy")
    clarity = prompt_float("Clarity")
    policy_safety = prompt_float("Policy/Safety Awareness")
    tone = prompt_float("Tone")

    total_score = tech_accuracy + clarity + policy_safety + tone

    notes = input("Notes (optional): ").strip()

    # Build row dict
    row = {
        "id": id_val,
        "domain": domain,
        "model_version": model_version,
        "tech_accuracy": tech_accuracy,
        "clarity": clarity,
        "policy_safety": policy_safety,
        "tone": tone,
        "total_score": total_score,
        "notes": notes,
    }

    # Ensure CSV exists & write if needed
    new_file = not RATINGS_FILE.exists()

    with RATINGS_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "domain",
                "model_version",
                "tech_accuracy",
                "clarity",
                "policy_safety",
                "tone",
                "total_score",
                "notes",
            ],
        )
        if new_file:
            writer.writeheader()  # create header if file didn't exist

        writer.writerow(row)

    print("\n✔ Rating added successfully!")
    print(f"✔ File updated: {RATINGS_FILE}\n")


if __name__ == "__main__":
    add_rating()
