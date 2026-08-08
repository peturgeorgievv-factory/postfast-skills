#!/usr/bin/env python3
"""Build the TikTok Agentic Hub variant of the PostFast skill.

The canonical skill (skills/postfast/SKILL.md, ~43k chars) exceeds TikTok's
15,000-20,000 character guideline for SKILL.md, and TikTok additionally requires
a README.md at the zip root plus a frontmatter `name` that matches the portal's
permanent Skill Name. This script derives a conforming package WITHOUT touching
the canonical skill:

  - keeps in SKILL.md: intro, Setup, Core Workflow, Social Inbox, Rate Limits,
    Media Specs, a top-5 gotchas digest, and a Supporting Files index
  - moves to references/: Common Patterns, Platform-Specific Controls, Helper
    Endpoints, Common Gotchas, Troubleshooting, Quick Reference, Tips for the Agent
  - swaps frontmatter for the TikTok one (name: postfast-social-media-management
    — PERMANENT on the portal, never change it without deleting the listing)
  - writes the TikTok-required README.md (incl. the mandatory disclosure that we
    do NOT use the TikTok for Business MCP Server)
  - zips everything with SKILL.md/README.md at the archive root

Update flow (see agent-hub memory reference_tiktok_agentic_hub):
  1. Edit the canonical skill, publish to ClawHub, git push (normal loop).
  2. Run:  python3 scripts/build-tiktok-variant.py [version] [outdir]
     e.g.  python3 scripts/build-tiktok-variant.py 1.16.0 /tmp/shared
     Zip name auto-bumps: postfast-social-media-management-skill-v<major>.zip
     per TikTok's rule "for subsequent updates, only change the version number".
  3. TT4B portal -> My Skills -> the skill -> upload new file version with the
     bumped semver + a Version Note. File updates re-enter review (5-7 business
     days); metadata-only edits (description/category/industry) do not.
"""
import re
import os
import shutil
import sys
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "skills", "postfast")
SKILL_NAME = "postfast-social-media-management"  # PERMANENT portal Skill Name

KEEP = ["Setup", "Core Workflow", "Social Inbox (Comments)", "Rate Limits",
        "Media Specs Quick Reference"]
MOVE = {
    "Common Patterns": "common-patterns.md",
    "Platform-Specific Controls": "platform-controls-summary.md",
    "Helper Endpoints": "helper-endpoints.md",
    "Common Gotchas": "gotchas.md",
    "Troubleshooting": "troubleshooting.md",
    "Quick Reference": "quick-reference.md",
    "Tips for the Agent": "agent-tips.md",
    "Supporting Resources": None,  # replaced by the generated index below
}

FRONTMATTER = '''---
name: "{name}"
description: "Use this Skill to schedule and publish TikTok posts (videos, photo carousels, TikTok app drafts), attach trending pre-cleared Commercial Music Library sounds to them, and manage the comments they receive, alongside 10 more platforms: Instagram, Facebook, X, YouTube, LinkedIn, Threads, Pinterest, Bluesky, Telegram, and Google Business Profile. Covers post creation with platform-specific controls, trending TikTok sound selection, media upload, the Social Inbox (read, reply to, hide, and triage comments on your own posts, including TikTok Business accounts), analytics, and follower history, all through the PostFast API. Use when a user wants to schedule social media posts, cross-post content, reply to comments, check post performance, or automate their posting workflow. PostFast is a SaaS tool; requires a PostFast workspace API key. Works on every plan including the 7-day free trial."
version: "{version}"
author: "Kohi Solutions Ltd (PostFast)"
use_case: "Content publishing and comment management"
homepage: "https://postfa.st"
---

# PostFast

Schedule social media posts across 11 platforms (TikTok first-class: videos, carousels, app drafts, comment management) from one API. SaaS, no self-hosting needed.
'''

TOP_GOTCHAS = """
## Top Gotchas (full list in references/gotchas.md)

- Auth header is `pf-api-key`, NOT `Authorization: Bearer` or `x-api-key`. Regenerating a key permanently invalidates the old one.
- X (Twitter) via API: hard platform limit of 5 posts per account per day. Do not exceed it.
- status=SCHEDULED requires a future `scheduledAt`; DRAFT must omit it. There is no instant publish: schedule a few minutes ahead.
- Media is required (even for drafts) on TikTok, YouTube, Instagram, Pinterest, and Google Business Profile; `mediaItems[].type` must match the file type.
- Inbox replies: derive reply ability from each conversation's server-computed `canReply`/`maxReplyLength`, never from assumed platform rules; repeated identical replies are rejected with a vary-the-wording error (rephrase, do not retry).
- TikTok sounds: `tiktokMusicSoundId` (from `GET /social-media/{id}/tiktok-sounds`, see references/helper-endpoints.md) and `tiktokAutoAddMusic` are mutually exclusive; sound ids rotate daily, fetch fresh per session; Business-API-connected TikTok accounts only.
"""

SUPPORTING = """
## Supporting Files

Longer reference material lives alongside this file: `references/common-patterns.md` (worked request patterns per platform), `references/platform-controls-summary.md` and `references/platform-controls.md` (every platform-specific control), `references/helper-endpoints.md` (Pinterest boards, YouTube playlists, GBP locations, follower history, place search, connect links), `references/gotchas.md`, `references/troubleshooting.md`, `references/quick-reference.md`, `references/agent-tips.md`, `references/api-reference.md`, `references/media-specs.md`, `references/upload-flow.md`, plus ready-to-adapt request bodies in `examples/` (see `examples/EXAMPLES.md`).
"""

README = """# PostFast Skill: Social Publishing and Comment Inbox

Schedule and publish posts to TikTok and 10 other social platforms, and manage the comments on your own posts, through one API that any AI agent can operate.

## Quick Start

1. Sign up at https://app.postfa.st/register (7-day free trial, no credit card).
2. In Workspace Settings, generate an API key.
3. Give your agent this Skill and set the environment variable:

```bash
export POSTFAST_API_KEY="your-api-key"
```

4. First prompts to try: "List my connected social accounts", then "Schedule a TikTok post for tomorrow 6pm with this video".

Base URL: `https://api.postfa.st` with auth header `pf-api-key`.

## Target platform

Agent-agnostic. Tested with Claude (Claude Code, Claude Desktop), ChatGPT, Cursor, and any agent that supports the SKILL.md format or plain REST instructions. No platform restrictions.

## Prerequisites and dependencies

- A PostFast account and a workspace API key (any plan, including the free trial).
- Runtime: none beyond an agent that can make HTTPS requests. Optionally, the same operations are available as MCP tools via the `postfast-mcp` npm package or PostFast's hosted MCP server.
- MCP disclosure: this Skill does NOT use the TikTok for Business MCP Server. It talks to PostFast's own public REST API (api.postfa.st), and optionally PostFast's own MCP server (postfast-mcp on npm, or the hosted server at mcp.postfa.st). PostFast itself connects to TikTok on the backend through TikTok's official, reviewed Content Posting and comment APIs (audited developer app); the agent never handles TikTok credentials.

## Configuration

- `POSTFAST_API_KEY` (required): workspace-scoped key from Workspace Settings. Rotating it invalidates the old key immediately.
- No other configuration. Defaults: the key's workspace; all connected accounts within it are addressable.

## Limitations and caveats

- The Social Inbox covers comments on your own posts (TikTok Business accounts, Instagram, Facebook Pages, Threads). It is not a DM inbox.
- X (Twitter) posting via API is limited by the platform to 5 posts per account per day.
- Media is required on TikTok, YouTube, Instagram, Pinterest, and Google Business Profile, even for drafts.
- All write operations are rate-limited per workspace, and repeated identical replies are rejected server-side with an instruction to vary the wording (anti-spam guard).

## Common errors and troubleshooting

- 403 on every call: wrong auth header. Use `pf-api-key`, not `Authorization: Bearer`.
- 429: rate limited; check the `Retry-After-*` headers and space batch calls ~1 second apart.
- A post stays unpublished: the account's `connectionStatus` is probably DISABLED; reconnect it in the PostFast dashboard.
- More: `references/troubleshooting.md` in this package, and https://postfa.st/docs.

## Maintainer and contact

Kohi Solutions Ltd (PostFast). Contact: petar@postfa.st. Docs: https://postfa.st/docs. Issue reports welcome by email.
"""


def main() -> None:
    canonical = open(os.path.join(SRC, "SKILL.md")).read()
    version = sys.argv[1] if len(sys.argv) > 1 else re.search(r"^version:\s*(\S+)", canonical, re.M).group(1)
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(REPO, "dist")
    build = os.path.join(REPO, "dist", "tiktok-build")
    shutil.rmtree(build, ignore_errors=True)
    os.makedirs(build)

    parts = re.split(r"(?m)^(## .+)$", canonical)
    sections = {parts[i].strip()[3:]: parts[i + 1] for i in range(1, len(parts), 2)}
    missing = [k for k in list(KEEP) + list(MOVE) if k not in sections]
    if missing:
        sys.exit(f"canonical SKILL.md sections renamed/missing: {missing} — update this script's KEEP/MOVE maps")

    out = FRONTMATTER.format(name=SKILL_NAME, version=version)
    for k in KEEP:
        out += f"\n## {k}" + sections[k]
    out += TOP_GOTCHAS + SUPPORTING

    desc = re.search(r'description: "(.*?)"\n', out, re.S).group(1)
    assert len(desc) <= 1536, f"frontmatter description {len(desc)} > 1536 chars"
    if not 15000 <= len(out) <= 20000:
        print(f"WARNING: variant SKILL.md is {len(out)} chars (TikTok guideline 15k-20k) — adjust KEEP/MOVE")

    open(os.path.join(build, "SKILL.md"), "w").write(out)
    open(os.path.join(build, "README.md"), "w").write(README)
    shutil.copytree(os.path.join(SRC, "references"), os.path.join(build, "references"))
    shutil.copytree(os.path.join(SRC, "examples"), os.path.join(build, "examples"))
    for k, fn in MOVE.items():
        if fn:
            open(os.path.join(build, "references", fn), "w").write(f"# {k} (PostFast Skill)\n" + sections[k])

    os.makedirs(outdir, exist_ok=True)
    zip_path = os.path.join(outdir, f"{SKILL_NAME}-skill-v{version.split('.')[0]}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(build):
            for f in sorted(files):
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, build))
    print(f"built {zip_path} ({os.path.getsize(zip_path)} bytes); SKILL.md {len(out)} chars; version {version}")


if __name__ == "__main__":
    main()
