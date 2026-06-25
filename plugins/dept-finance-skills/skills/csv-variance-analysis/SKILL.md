---
name: csv-variance-analysis
description: Analyzes a finance category CSV for budget-vs-actual variance and flags lines over a threshold, with a short written summary. Use when a user asks to review variance in a category export.
---
# CSV variance analysis
Given a finance category CSV (with budget and actual columns):
1. For each line, compute variance = actual − budget and pct = variance / budget.
2. Flag any line whose absolute pct breaches the threshold (default 10%).
3. Summarize the flagged lines in plain language for a non-finance reader.
