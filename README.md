# PostFast Agent Skills

Official agent skills for [PostFast](https://postfa.st), the social media scheduling platform your AI agent can operate. Schedule and publish posts to 11 platforms (Instagram, TikTok, X, LinkedIn, Facebook, YouTube, Threads, Pinterest, Bluesky, Telegram, and Google Business Profile) through the PostFast API.

The `postfast` skill follows the [Agent Skills open standard](https://agentskills.io) (SKILL.md), so it works in any skills-compatible agent.

## Install

**Vercel skills CLI** (Claude Code, Cursor, Codex, GitHub Copilot, Gemini CLI, and 70+ other agents):

```bash
npx skills add peturgeorgievv-factory/postfast-skills
```

**Hermes Agent** (as a GitHub tap, or via ClawHub):

```bash
hermes skills tap add peturgeorgievv-factory/postfast-skills
hermes skills install peturgeorgievv-factory/postfast-skills/postfast
# or from ClawHub:
hermes skills search postfast --source clawhub
```

**OpenClaw / ClawHub** (use the scoped ref):

```bash
clawhub install @peturgeorgievv/postfast
```

## Setup

1. Sign up at [app.postfa.st/register](https://app.postfa.st/register) (7-day free trial, no credit card)
2. Go to Workspace Settings and generate an API key
3. Set it as an environment variable:

```bash
export POSTFAST_API_KEY="your-api-key"
```

The skill teaches your agent the full PostFast API: scheduling, cross-posting, media uploads, drafts, listing posts by account, platform, status or date, deleting posts one at a time or up to 100 per call, analytics (including video watch time and Instagram save rate), follower history, TikTok trending sounds, the Social Inbox for comments, client connect links, and the per-endpoint rate limits.

## What's inside

```
skills/postfast/
├── SKILL.md          # The skill: full API workflow instructions
├── references/       # API reference, platform controls, media specs, upload flow
└── examples/         # 31 ready-to-use request examples
```

## Guides

- [Hermes Agent setup](https://postfa.st/api-integrations/hermes)
- [OpenClaw setup](https://postfa.st/api-integrations/openclaw)
- [NanoClaw setup](https://postfa.st/api-integrations/nanoclaw)
- [MCP server](https://postfa.st/api-integrations/mcp) (if you prefer MCP tools over a skill)
- [Hermes Agent vs OpenClaw comparison](https://postfa.st/blog/hermes-agent-vs-openclaw)
- [API documentation](https://postfa.st/docs)

## Versioning

This repository is the canonical source. The same skill is published to ClawHub as [@peturgeorgievv/postfast](https://clawhub.ai/peturgeorgievv/skills/postfast). Versions follow the `version` field in SKILL.md frontmatter.

## License

MIT-0. Free to use, modify, and redistribute. No attribution required.
