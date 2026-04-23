![Agent Search Skills Banner](../images/openclaw-search-skills-banner.png)

<div align="center">

# Agent Search Skills

English | [简体中文](../README.md)

**A reusable search and extraction skill pack for Claude Code, Codex, OpenCode, and other agent runtimes with shell and optional web capabilities.**

[![Agent-ready](https://img.shields.io/badge/Agent-ready-0A84FF)](#compatibility-model)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![search-layer](https://img.shields.io/badge/search--layer-v3.1-7C3AED)](../search-layer/SKILL.md)
[![content-extract](https://img.shields.io/badge/content--extract-MinerU%20Fallback-14B8A6)](../content-extract/SKILL.md)

</div>

> This repo started as an OpenClaw-focused package. It now targets generic agent runtimes, while keeping the legacy `~/.openclaw/...` paths as compatibility fallbacks.

## Overview

`search-skills` provides three composable capabilities:

| Skill | Purpose |
|-------|---------|
| **[search-layer](../search-layer/)** | Multi-source search orchestration over Exa, Tavily, and Grok, with the runtime's native web search acting as the broad-web lane when available. |
| **[content-extract](../content-extract/)** | URL → clean Markdown. Uses the runtime's native fetch/browser path first, then falls back to MinerU for anti-bot or poorly extracted pages. |
| **[mineru-extract](../mineru-extract/)** | A wrapper around the official [MinerU](https://mineru.net) API for high-fidelity parsing of HTML, PDFs, Office files, and images. |

They fit into a runtime-agnostic flow:

```text
Any Agent Runtime
├── search-layer       multi-source retrieval / intent scoring / citation tracking
├── content-extract    URL → Markdown / anti-bot fallback
│   └── mineru-extract high-fidelity parsing (HTML / PDF / Office / OCR)
└── Runtime built-ins  search / fetch / browser / shell
```

## Compatibility Model

These skills no longer assume a specific tool name. They depend on capability classes:

| Capability | Used for | If your runtime does not have it |
|------------|----------|----------------------------------|
| `search` | broad web recall and current-event verification | run `search-layer/scripts/search.py` directly and rely on Exa / Tavily / Grok |
| `fetch` | cheap body extraction and probe passes | skip directly to `content-extract` or `mineru-extract` |
| `browser` | JS-heavy pages and interactive sites | fall back to `mineru-extract`, or ask the user for an accessible copy |
| `shell` | running the repo scripts | required |

That makes this repo a practical fit for:

- Claude Code
- Codex
- OpenCode
- any agent runtime that can read `SKILL.md`, run shell commands, and optionally browse the web

If your runtime treats "skills" as prompt files rather than a formal package type, you can still reuse these `SKILL.md` files and map the capability names to your local tools.

## Installation

### Generic install

```bash
git clone https://github.com/blessonism/openclaw-search-skills.git
cd openclaw-search-skills
```

Then choose either approach:

1. Symlink or copy individual skill directories into your runtime's skills or prompts directory.
2. Keep the repo as-is and point your runtime to the `SKILL.md` files directly.

Recommended environment variable:

```bash
export SEARCH_SKILLS_ROOT="$PWD"
```

## Configuration

### Search credentials

`search-layer` looks for credentials in this order:

1. bundled repo example: `search-layer/search.json`
2. `SEARCH_SKILLS_CREDENTIALS`
3. `AGENT_CREDENTIALS_PATH`
4. `./credentials/search.json`
5. `~/.agent-skills/credentials/search.json`
6. legacy fallback: `~/.openclaw/credentials/search.json`

Recommended: edit `search-layer/search.json` directly:

```json
{
  "exa": "your-exa-key",
  "tavily": "your-tavily-key",
  "grok": {
    "apiUrl": "https://api.x.ai/v1",
    "apiKey": "your-grok-key",
    "model": "grok-4.1-fast"
  }
}
```

If `search-layer/search.json` still contains placeholder values such as `your-exa-key`, the loader ignores them instead of treating them as real credentials.

Environment variables override file values:

```bash
export EXA_API_KEY="your-exa-key"
export EXA_API_BASE="https://api.exa.ai"
export TAVILY_API_KEY="your-tavily-key"
export GROK_API_URL="https://api.x.ai/v1"
export GROK_API_KEY="your-grok-key"
export GROK_MODEL="grok-4.1-fast"
```

### Workspace

`mineru-extract` writes cache and downloaded artifacts to a workspace directory. Resolution order:

1. `SEARCH_SKILLS_WORKSPACE`
2. `AGENT_WORKSPACE`
3. legacy fallback: `OPENCLAW_WORKSPACE`
4. default: `~/.agent-skills/workspace`

### MinerU token

For WeChat, Zhihu, Office files, or PDF extraction, configure `mineru-extract/.env`:

```bash
cp mineru-extract/.env.example mineru-extract/.env
```

```env
MINERU_TOKEN=your_token_here
MINERU_API_BASE=https://mineru.net
```

## Quick Usage

### 1. Multi-source search

```bash
python3 search-layer/scripts/search.py "Codex agent runtime search skill" \
  --mode deep --intent exploratory --num 5
```

### 2. Citation tracking from search results

```bash
python3 search-layer/scripts/search.py "Claude Code config bug" \
  --mode deep --intent status --extract-refs
```

```bash
python3 search-layer/scripts/fetch_thread.py "https://github.com/owner/repo/issues/123"
```

### 3. URL → Markdown

```bash
python3 content-extract/scripts/content_extract.py \
  --url "https://mp.weixin.qq.com/s/example"
```

### 4. Direct MinerU parsing

```bash
python3 mineru-extract/scripts/mineru_parse_documents.py \
  --file-sources "https://example.com/doc.pdf" \
  --emit-markdown --max-chars 20000
```

## Runtime Contract

The repo now uses capability semantics instead of runtime-specific tool names:

- `search-layer` assumes the runtime may have a web-search primitive, but it can operate entirely through scripts when needed.
- `content-extract` assumes a cheap fetch probe is preferable, but direct script execution is still valid.
- `mineru-extract` depends only on shell and network access.

You do not need to mimic OpenClaw. You only need to map your runtime's search, fetch, and browser capabilities onto the same behavior.

## Compatibility Notes

- Legacy `~/.openclaw/...` credentials and workspace paths still work.
- The GitHub repository name remains unchanged to avoid breaking existing references.
- README files, `SKILL.md` contracts, and script defaults now describe generic agent usage.

## License

MIT
