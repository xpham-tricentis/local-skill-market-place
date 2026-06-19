---
name: jira-to-test-plan
description: Automatically converts a pasted Jira ticket into a structured test plan in Markdown.
  Use this skill whenever the user pastes or shares a Jira ticket (Epic, Task, or Sub-task),
  mentions a ticket ID with description, or asks to "generate a test plan", "write test cases",
  or "create a QA plan" from a ticket or requirement. Trigger even if the user doesn't say
  "skill" — any pasted Jira-style content (with fields like Summary, Description, Acceptance
  Criteria, or a ticket key like PROJ-123) is a strong signal to use this skill immediately.
---

# Jira to Test Plan Skill

Converts a pasted Jira ticket into a structured, ready-to-use Markdown test plan.

---

## Step 1: Parse the Ticket

Read the pasted content and extract as many of the following fields as are present:

| Field | Notes |
|---|---|
| **Ticket key** | e.g. `PROJ-123` |
| **Ticket type** | Epic, Task, or Sub-task — infer from content if not stated |
| **Summary / Title** | The one-line description of the ticket |
| **Description** | The full body of the ticket |
| **Acceptance Criteria** | May be listed as bullet points, numbered items, or "Given/When/Then" |
| **Labels / Components** | If present, use to infer affected area |
| **Child tickets** | If an Epic lists child stories or tasks, note them (but don't expand them) |

If any critical fields (Summary, Description) are missing or ambiguous, make a reasonable inference and note it in the output with a `> ⚠️ Assumed: ...` blockquote.

---

## Step 2: Determine Ticket Type and Choose Output Structure

### If the ticket is an **Epic**:
Generate a **high-level test plan** covering the epic's overall scope (see Template A below).

### If the ticket is a **Task or Sub-task**:
Generate **detailed step-by-step test cases** (see Template B below).

If the type is unclear, default to Template B (detailed test cases) and add a note.

---

## Template A — Epic: High-Level Test Plan

```markdown
# Test Plan: [Summary / Title]
**Ticket:** [Key] | **Type:** Epic

---

## 1. Overview
[1–2 sentence summary of what this epic delivers and why it matters from a testing perspective.]

## 2. Scope
**In scope:**
- [Feature / behaviour area 1]
- [Feature / behaviour area 2]

**Out of scope:**
- [Anything explicitly excluded or deferred]

## 3. Test Objectives
- Verify that [main goal 1]
- Verify that [main goal 2]
- Ensure [non-functional concern if relevant, e.g. performance, security]

## 4. Test Areas & High-Level Scenarios

### [Area 1 — e.g. "User Authentication"]
- [ ] [Scenario: happy path]
- [ ] [Scenario: edge case]
- [ ] [Scenario: error/negative case]

### [Area 2 — e.g. "Permissions & Access Control"]
- [ ] [Scenario]
- [ ] [Scenario]

## 5. Dependencies & Risks
| Item | Detail |
|---|---|
| Dependency | [e.g. requires API X to be deployed] |
| Risk | [e.g. unclear acceptance criteria for area Y] |

## 6. Notes
[Any assumptions, open questions, or links to related tickets.]
```

---

## Template B — Task / Sub-task: Step-by-Step Test Cases

```markdown
# Test Cases: [Summary / Title]
**Ticket:** [Key] | **Type:** [Task / Sub-task]

---

## Context
[1–2 sentences describing what this ticket implements, to give the tester context.]

## Acceptance Criteria Coverage
[List each acceptance criterion from the ticket and confirm it maps to at least one test case below. If AC is missing, note it.]

---

## Test Cases

### TC-01: [Short descriptive name — happy path]
**Preconditions:** [Any setup required before the test]

| Step | Action | Expected Result |
|---|---|---|
| 1 | [What the tester does] | [What should happen] |
| 2 | | |
| 3 | | |

---

### TC-02: [Short descriptive name — variation or alternate flow]
**Preconditions:** [...]

| Step | Action | Expected Result |
|---|---|---|
| 1 | | |
| 2 | | |

---

### TC-03: [Short descriptive name — negative / error case]
**Preconditions:** [...]

| Step | Action | Expected Result |
|---|---|---|
| 1 | | |
| 2 | | |

---

## Notes
[Assumptions, open questions, or links to related tickets.]
```

---

## Guidelines for Generating Test Cases

- **Coverage**: Always include at least one happy-path case. Add negative/error cases when the description mentions validation, permissions, error handling, or constraints.
- **Specificity**: Make actions concrete and unambiguous. Prefer "Click the **Submit** button" over "Submit the form."
- **Expected results**: Must be observable and verifiable — avoid vague outcomes like "works correctly."
- **AC mapping**: For Tasks, trace each acceptance criterion to at least one test case. If an AC can't be tested as written, flag it.
- **Quantity**: Aim for 3–6 test cases for a Task. For Epics, aim for 3–5 test areas with 2–4 scenarios each. Scale with ticket complexity.
- **Numbering**: Use `TC-01`, `TC-02`, etc. for Tasks; scenarios in Epics don't need numbering.
- **Tricentis context**: Given the software testing domain, feel free to reference testing concepts (boundary value analysis, equivalence partitioning) in the Notes section where relevant.

---

## Gantt Chart

After generating the Markdown test plan for a **Task or Sub-task**, always run the bundled
`scripts/generate_gantt.py` to produce a PNG Gantt chart. Never write chart code yourself —
always call this script. The steps are the same every time:

### Step 1 — Build the JSON input file

From the test cases you already generated, write a JSON file to `/tmp/test_cases.json`
using exactly this schema:

```json
{
  "ticket": "<TICKET-KEY>",
  "title":  "<One-line ticket summary>",
  "test_cases": [
    {"id": "TC-01", "name": "<short name>", "duration": <hours as int>, "start": 0},
    {"id": "TC-02", "name": "<short name>", "duration": <hours as int>, "start": 0}
  ]
}
```

Rules:
- `duration` — estimate in whole hours; use 1 for simple cases, 2–3 for complex ones
- `start` — set all values to `0` to let the script auto-stack cases sequentially,
  or use explicit offsets to show parallel execution
- Do not omit any field; all four keys are required per test case

### Step 2 — Install dependency (if needed)

```bash
pip install matplotlib --break-system-packages -q
```

### Step 3 — Run the script

```bash
python scripts/generate_gantt.py --data-file /tmp/test_cases.json --output /tmp/gantt_chart.png
```

### Step 4 — Present the chart

```python
present_files(["/tmp/gantt_chart.png"])
```

For **Epics**, skip the chart — the high-level plan doesn't have individual test cases to plot.

---

## Output Rules

- Output the full test plan in **Markdown**, rendered in chat — no file download unless the user asks.
- Do not add preamble like "Here is your test plan:". Start directly with the `# Test Plan:` or `# Test Cases:` heading.
- If the ticket is very short or lacks detail, generate what you can and flag gaps clearly with `> ⚠️` blockquotes.
- If the user pastes multiple tickets at once, generate a separate plan for each, separated by `---`.