# Claude Code Skills Marketplace

A curated marketplace of Claude Code skills and plugins — fully self-contained, no git submodules.

## Installation

Install any entry directly from this marketplace:

```
/plugin install {name}@quick-sort/skills
```

Or browse available entries using `/plugin > Discover`.

## Structure

- **`skills/`** — Standalone skill packages (one skill per entry, `SKILL.md` at root)
- **`plugins/`** — Full plugin packages (multi-component: skills + agents + commands + hooks)
- **`scripts/`** — Upstream sync tooling (`sync.py` + `upstream.json`)

All content is vendored directly into this repository. Former git submodules have been
flattened so that a plain `git clone` (which is what Claude Code does when adding a
marketplace) gets every entry's files.

## Upstream Sources

Vendored content is re-syncable from upstream via `scripts/sync.py`:

| Vendored | Upstream |
|----------|----------|
| `skills/fireworks-tech-graph` | [yizhiyanhua-ai/fireworks-tech-graph](https://github.com/yizhiyanhua-ai/fireworks-tech-graph) |
| 20 Anthropic skills (`docx`, `pdf`, `pptx`, `xlsx`, `mcp-builder`, `skill-creator`, …) | [anthropics/skills](https://github.com/anthropics/skills) |
| 13 official plugins (`plugin-dev`, `code-review`, `feature-dev`, `hookify`, …) | [anthropics/claude-code](https://github.com/anthropics/claude-code) `plugins/` |
| 17 MiniMax skills (`frontend-dev`, `shader-dev`, `gif-sticker-maker`, …) + `plugins/pptx-plugin` | [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) |
| `plugins/n8n-mcp-skills` (15 skills + hooks layer) | [czlonkowski/n8n-skills](https://github.com/czlonkowski/n8n-skills) |

Locally maintained (never synced): `architecture-diagram`, `odoo-19`, `find-skills`,
the hand-written `plugin.json` manifests for `plugin-dev` and `n8n-mcp-skills`.

### Syncing from upstream

```bash
scripts/sync.py --check    # report which upstreams have new commits
scripts/sync.py            # sync everything to latest upstream heads
scripts/sync.py minimax    # sync sources whose repo URL matches "minimax"
```

Sync updates `scripts/upstream.json` with the new SHAs. After syncing, review the diff
and update `.claude-plugin/marketplace.json` if versions/descriptions changed.

## Contributing

1. Fork this repository
2. Add your skill under `skills/{skill-name}/` with a `SKILL.md`, or a full plugin under `plugins/{name}/` with `.claude-plugin/plugin.json`
3. Register it in `.claude-plugin/marketplace.json` (one entry per installable item)
4. Submit a pull request

## Documentation

For more information on developing Claude Code skills, see the [official documentation](https://code.claude.com/docs/en/plugins).
