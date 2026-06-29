#!/usr/bin/env python3
"""
generate_gantt.py — Test Execution Gantt Chart Generator
=========================================================
Part of the jira-to-test-plan skill. This script is the single source of truth
for chart generation — Claude never writes chart code; it always calls this file.

Usage (Claude calls this after parsing the ticket):
    python scripts/generate_gantt.py --data-file /tmp/test_cases.json --output gantt_chart.png

Input JSON schema (write to a temp file, then pass with --data-file):
    {
      "ticket":     "PROJ-88",
      "title":      "Add input validation to user registration form",
      "test_cases": [
        {"id": "TC-01", "name": "Successful registration (happy path)", "duration": 2, "start": 0},
        {"id": "TC-02", "name": "Invalid email format rejected",         "duration": 1, "start": 2},
        {"id": "TC-03", "name": "Password strength validation",          "duration": 2, "start": 2},
        {"id": "TC-04", "name": "Duplicate username rejected",           "duration": 1, "start": 4}
      ]
    }

Fields:
    ticket      — Jira ticket key shown in the chart title (e.g. "PROJ-88")
    title       — Ticket summary shown as chart subtitle
    test_cases  — List of test case objects:
        id        — Display ID shown on the bar (e.g. "TC-01")
        name      — Short description of the test case
        duration  — Estimated duration in hours (integer or float)
        start     — Start hour offset from 0 (use 0 for sequential auto-layout)

Auto-layout:
    If all "start" values are 0, the chart auto-stacks cases sequentially
    (i.e. TC-02 starts where TC-01 ends). Set explicit "start" values to
    show parallel execution.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ImportError:
    print("ERROR: matplotlib is required.  Run:  pip install matplotlib")
    sys.exit(1)

# ── Colour palette (consistent across all charts) ──────────────────────────
PALETTE = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2",
    "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD",
]

# ── Fallback sample data (used only when no --data-file is supplied) ────────
SAMPLE_DATA = {
    "ticket": "PROJ-00",
    "title": "Sample Test Plan (replace with real ticket data)",
    "test_cases": [
        {"id": "TC-01", "name": "Happy path end-to-end",          "duration": 2, "start": 0},
        {"id": "TC-02", "name": "Input validation — email",        "duration": 1, "start": 2},
        {"id": "TC-03", "name": "Input validation — password",     "duration": 2, "start": 2},
        {"id": "TC-04", "name": "Duplicate username rejection",    "duration": 1, "start": 4},
        {"id": "TC-05", "name": "API bypass / security check",     "duration": 3, "start": 5},
    ],
}


def auto_layout(test_cases):
    """If all starts are 0, stack cases sequentially."""
    if all(tc.get("start", 0) == 0 for tc in test_cases):
        cursor = 0
        for tc in test_cases:
            tc["start"] = cursor
            cursor += tc["duration"]
    return test_cases


def build_chart(data: dict, output_path: str):
    test_cases = auto_layout(data.get("test_cases", []))
    ticket     = data.get("ticket", "")
    title_text = data.get("title", "")
    n          = len(test_cases)

    if n == 0:
        print("ERROR: test_cases list is empty.")
        sys.exit(1)

    fig, ax = plt.subplots(figsize=(13, max(4, n * 0.75 + 2.5)))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    for i, tc in enumerate(test_cases):
        color = PALETTE[i % len(PALETTE)]
        ax.barh(
            y=i,
            width=tc["duration"],
            left=tc["start"],
            height=0.55,
            color=color,
            edgecolor="white",
            linewidth=1.0,
            zorder=3,
        )
        # Duration label inside bar
        bar_center_x = tc["start"] + tc["duration"] / 2
        ax.text(
            bar_center_x, i,
            f'{tc["duration"]}h',
            va="center", ha="center",
            color="white", fontsize=8.5, fontweight="bold",
            zorder=4,
        )

    # Y-axis
    y_labels = [f'{tc["id"]}  {tc["name"]}' for tc in test_cases]
    ax.set_yticks(range(n))
    ax.set_yticklabels(y_labels, fontsize=9)
    ax.invert_yaxis()
    ax.tick_params(axis="y", length=0)

    # X-axis
    max_end = max(tc["start"] + tc["duration"] for tc in test_cases)
    ax.set_xlim(0, max_end + 0.5)
    ax.set_xlabel("Estimated Duration (hours)", fontsize=10, labelpad=8)
    ax.xaxis.set_major_locator(plt.MultipleLocator(1))
    ax.grid(axis="x", linestyle="--", alpha=0.35, zorder=0)
    ax.set_axisbelow(True)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    # Title block
    chart_title = f"Test Execution Plan — {ticket}" if ticket else "Test Execution Plan"
    ax.set_title(chart_title, fontsize=14, fontweight="bold", pad=6, loc="left")
    if title_text:
        ax.annotate(
            title_text,
            xy=(0, 1), xycoords="axes fraction",
            xytext=(0, 18), textcoords="offset points",
            fontsize=9, color="#555555", ha="left",
        )

    # Total hours
    total = sum(tc["duration"] for tc in test_cases)
    ax.annotate(
        f"Total estimated: {total}h",
        xy=(1, 0), xycoords="axes fraction",
        xytext=(-4, -28), textcoords="offset points",
        ha="right", va="top", fontsize=9, color="#555555",
    )

    plt.tight_layout(rect=[0, 0.02, 1, 0.97])
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✅  Chart saved → {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Gantt chart from a JSON test plan."
    )
    parser.add_argument(
        "--data-file",
        metavar="PATH",
        help="Path to a JSON file containing ticket + test_cases (see schema in docstring)",
    )
    parser.add_argument(
        "--output",
        default="gantt_chart.png",
        metavar="PATH",
        help="Output PNG file path (default: gantt_chart.png)",
    )
    args = parser.parse_args()

    if args.data_file:
        data_path = Path(args.data_file)
        if not data_path.exists():
            print(f"ERROR: File not found: {data_path}")
            sys.exit(1)
        with open(data_path) as f:
            data = json.load(f)
        print(f"📋  Loaded {len(data.get('test_cases', []))} test case(s) from {data_path}")
    else:
        print("ℹ️   No --data-file supplied — using built-in sample data.")
        data = SAMPLE_DATA

    build_chart(data, args.output)


if __name__ == "__main__":
    main()
