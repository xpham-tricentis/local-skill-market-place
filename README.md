# Skill Studio Marketplace

Private Claude Code plugin marketplace for internal **Skill Studio** departments.

Each department ships as a plugin under [`plugins/`](plugins/), and each plugin
bundles one or more prompt-only skills (a single `SKILL.md` each — no scripts,
no MCP servers, no branded tools).

## Departments

| Department | Plugin |
| --- | --- |
| Finance | `dept-finance-skills` |
| Comms | `dept-comms-skills` |
| People Ops | `dept-people-ops-skills` |
| Quality Engineering | `dept-quality-engineering-skills` |
| Sales Ops | `dept-sales-ops-skills` |

## Using the marketplace

Add it in Claude Code, then install the department plugins you need:

```
/plugin marketplace add <this-repo>
/plugin install dept-finance-skills@skills-marketplace
```

The marketplace manifest lives at
[`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json). See
[`CHANGELOG.md`](CHANGELOG.md) for version history.
