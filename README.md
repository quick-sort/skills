# Claude Code Skills Marketplace

A curated directory of high-quality skills and plugins for Claude Code.

## Installation

Install skills directly from this marketplace:

```
/plugin install {skill-name}@{owner}/skills
```

Or browse available skills using `/plugin > Discover`.

## Structure

- **`plugins/`** - Individual skill and plugin packages (marketplace-registered)
- **`skills/`** - Standalone skills (installed locally, not published to marketplace)

## Available Skills

| Skill | Category | Description |
|-------|----------|-------------|
| [example-skill](plugins/example-skill/) | example | Example skill demonstrating the Claude Code marketplace plugin structure |
| [fireworks-tech-graph](skills/fireworks-tech-graph/) | developer-tools | Generate production-quality SVG technical diagrams (architecture, data flow, UML, network topology) exported as SVG+PNG |
| [architecture-diagram](skills/architecture-diagram/) | diagrams | Create professional dark-themed architecture diagrams as standalone HTML files with inline SVG |
| [odoo-19](skills/odoo-19/) | erp-crm | Odoo 19 development knowledge base with 18 specialized guides covering the full module development lifecycle |

## Contributing

### Submitting a Skill

1. Fork this repository
2. Add your skill under `plugins/{skill-name}/`
3. Include a `.claude-plugin/plugin.json` with metadata
4. Add your skill to `marketplace.json`
5. Submit a pull request

### Skill Structure

Each skill should follow this structure:

```
plugins/
└── my-skill/
    ├── .claude-plugin/
    │   └── plugin.json      # Skill metadata
    ├── skills/
    │   └── my-skill/
    │       └── SKILL.md     # Skill content
    └── README.md            # Documentation
```

### Standalone Skills

Standalone skills live under `skills/` and are installed locally. They should include a `SKILL.md` with YAML frontmatter:

```yaml
---
name: my-skill
description: >-
  Multi-line description with trigger keywords that activate the skill.
---
```

## Documentation

For more information on developing Claude Code skills, see the [official documentation](https://code.claude.com/docs/en/plugins).
