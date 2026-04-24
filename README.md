# Claude Code Skills Marketplace

A curated directory of high-quality skills and plugins for Claude Code.

## Installation

Install skills directly from this marketplace:

```
/plugin install {skill-name}@{owner}/skills
```

Or browse available skills using `/plugin > Discover`.

## Structure

- **`plugins/`** - Individual skill and plugin packages

## Available Skills

No skills available yet. Browse the marketplace to discover and add skills.

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

## Documentation

For more information on developing Claude Code skills, see the [official documentation](https://code.claude.com/docs/en/plugins).
