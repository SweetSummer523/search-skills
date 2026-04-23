# Agent Search Skills

[English](./docs/README_EN.md) | 简体中文

**面向 Claude Code、Codex、OpenCode 等具备 shell / web 能力 Agent 的多源搜索与内容提取 skills。**

[![Agent-ready](https://img.shields.io/badge/Agent-ready-0A84FF)](#兼容模型)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![search-layer](https://img.shields.io/badge/search--layer-v3.1-7C3AED)](./search-layer/SKILL.md)
[![content-extract](https://img.shields.io/badge/content--extract-MinerU%20Fallback-14B8A6)](./content-extract/SKILL.md)

</div>

> 原仓库（[openclaw-search-skills](https://github.com/blessonism/openclaw-search-skills)）最初为 OpenClaw 设计；现在已改造成更通用的 agent skill 包，保留旧路径兼容，但文档和默认约定不再绑定单一运行时。

## 概述

`search-skills` 提供三块可组合能力：

| Skill | 作用 |
|-------|------|
| **[search-layer](./search-layer/)** | 多源搜索编排，聚合 Exa、Tavily、Grok，并允许 Agent 自己的内置 web search 作为广域召回层。 |
| **[content-extract](./content-extract/)** | URL → 干净 Markdown。优先走运行时原生抓取，遇到反爬或正文缺失时再降级到 MinerU。 |
| **[mineru-extract](./mineru-extract/)** | 封装官方 [MinerU](https://mineru.net) API，把 HTML、PDF、Office、图片等解析成 Markdown 与结构化产物。 |

它们可以组合成一条通用工作流：

```text
任意 Agent Runtime
├── search-layer       多源检索 / 意图识别 / 结果排序 / 引用追踪
├── content-extract    URL → Markdown / 反爬站点降级
│   └── mineru-extract 高保真解析 (HTML / PDF / Office / OCR)
└── Runtime built-ins  search / fetch / browser / shell
```

## 兼容模型

这套 skills 不再假设某个固定工具名，而是依赖下面几类能力：

| 能力 | 用途 | 没有该能力时怎么办 |
|------|------|--------------------|
| `search` | 广域网页召回、快速确认最新信息 | 直接运行 `search-layer/scripts/search.py`，使用 Exa / Tavily / Grok |
| `fetch` | 拉正文、做低成本 probe | 让用户提供 URL，或直接走 `content-extract` / `mineru-extract` |
| `browser` | JS 渲染页面、需要交互的站点 | 直接降级到 `mineru-extract`，或让用户提供可访问页面 |
| `shell` | 执行本仓库脚本 | 必需 |

因此它适合：

- Claude Code
- Codex
- OpenCode
- 任何支持读取 `SKILL.md`、执行 shell、可选浏览网页的 Agent runtime

如果某个 Agent 的“skills”机制只是提示词注入，也可以直接复用这些 `SKILL.md`，再按本地工具名映射 `search/fetch/browser` 能力即可。

## 安装

### 告诉Agent
</div>

> 帮我安装这个Skill：https://github.com/SweetSummer523/search-skills

### 通用安装

```bash
git clone https://github.com/SweetSummer523/search-skills.git
# 链接或者复制到Agent的skills目录（以Claude Code为例，将<search-skills path>替换为上一条指令clone的路径）
ln -s <search-skills path>/search-layer ~/.claude/skills/search-layer
ln -s <search-skills path>/content-extract ~/.claude/skills/content-extract
ln -s <search-skills path>/mineru-extract ~/.claude/skills/mineru-extract
```

## 配置

### 搜索凭据

`search-layer` 会按下面的优先级找配置：

1. 仓库内置示例文件：`search-layer/search.json`
2. `SEARCH_SKILLS_CREDENTIALS`
3. `AGENT_CREDENTIALS_PATH`
4. `./credentials/search.json`
5. `~/.agent-skills/credentials/search.json`
6. 旧版兼容：`~/.openclaw/credentials/search.json`

推荐直接编辑仓库里的 `search-layer/search.json`：

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

如果 `search-layer/search.json` 里仍然是 `your-exa-key` 这类占位值，加载器会自动忽略，不会把它当成真实凭据。

也支持环境变量覆盖：

```bash
export EXA_API_KEY="your-exa-key"
export EXA_API_BASE="https://api.exa.ai"
export TAVILY_API_KEY="your-tavily-key"
export GROK_API_URL="https://api.x.ai/v1"
export GROK_API_KEY="your-grok-key"
export GROK_MODEL="grok-4.1-fast"
```

### Workspace

`mineru-extract` 会把缓存和下载结果写到 workspace。查找顺序为：

1. `SEARCH_SKILLS_WORKSPACE`
2. `AGENT_WORKSPACE`
3. 旧版兼容：`OPENCLAW_WORKSPACE`
4. 默认：`~/.agent-skills/workspace`

### MinerU Token

如需解析微信、知乎、Office 或 PDF，可在 `mineru-extract/.env` 中配置：

```bash
cp mineru-extract/.env.example mineru-extract/.env
```

```env
MINERU_TOKEN=your_token_here
MINERU_API_BASE=https://mineru.net
```

## 快速使用

### 1. 多源搜索

```bash
python3 search-layer/scripts/search.py "Codex agent runtime search skill" \
  --mode deep --intent exploratory --num 5
```

### 2. 搜索结果引用追踪

```bash
python3 search-layer/scripts/search.py "Claude Code config bug" \
  --mode deep --intent status --extract-refs
```

```bash
python3 search-layer/scripts/fetch_thread.py "https://github.com/owner/repo/issues/123"
```

### 3. URL 转 Markdown

```bash
python3 content-extract/scripts/content_extract.py \
  --url "https://mp.weixin.qq.com/s/example"
```

### 4. 直接调用 MinerU

```bash
python3 mineru-extract/scripts/mineru_parse_documents.py \
  --file-sources "https://example.com/doc.pdf" \
  --emit-markdown --max-chars 20000
```

## 对 Agent 的约定

这些 skills 现在统一使用“能力语义”而不是“工具名语义”：

- `search-layer` 假设 runtime 有某种网页搜索能力；没有的话就完全走脚本搜索源。
- `content-extract` 假设 runtime 能先做一次廉价的 fetch probe；如果做不到，直接调用脚本也可以。
- `mineru-extract` 不依赖特定 Agent，只依赖 shell 和网络。

换句话说，你不需要把运行时伪装成 OpenClaw；只需要把本地的搜索、抓取、浏览能力映射到相同语义即可。

## 兼容性说明

- 保留对旧版 `~/.openclaw/...` 凭据与 workspace 路径的兼容。
- 仓库名暂未变更，避免打断现有引用和安装链接。
- README、`SKILL.md` 和脚本默认值已经改成 Agent 通用表述。

## 给 AI Agent 读的安装协议

当用户说：

> 帮我安装这个skill：https://github.com/SweetSummer523/search-skills

请按下面规则执行，不要自行猜测“仓库根目录就是一个 skill”：

1. 这个仓库包含 **3 个独立 skill**，必须分别安装：
   - `search-layer`
   - `content-extract`
   - `mineru-extract`
2. **不要**把仓库根目录 `search-skills/` 当成单个 skill 安装，因为仓库根目录本身不是一个可安装 skill，真正的 skill 目录是上面三个子目录；每个子目录里都带有自己的 `SKILL.md`。
3. 安装时必须保留每个 skill 目录内的全部 supporting files，而不是只复制 `SKILL.md`。
4. 如果 runtime 支持 symbolic link，优先用 link；否则复制目录也可以。

### Claude Code 安装规则

把这 3 个目录安装到：

- `~/.claude/skills/search-layer`
- `~/.claude/skills/content-extract`
- `~/.claude/skills/mineru-extract`

示例：

```bash
git clone https://github.com/SweetSummer523/search-skills.git
ln -s <search-skills path>/search-layer ~/.claude/skills/search-layer
ln -s <search-skills path>/content-extract ~/.claude/skills/content-extract
ln -s <search-skills path>/mineru-extract ~/.claude/skills/mineru-extract
```

### Codex 安装规则

把这 3 个目录安装到：

- `~/.codex/skills/search-layer`
- `~/.codex/skills/content-extract`
- `~/.codex/skills/mineru-extract`

如果你使用 Codex 的 GitHub skill installer，必须传入子目录路径，而不是只传仓库根 URL。等价目标如下：

- `search-layer`
- `content-extract`
- `mineru-extract`

### 安装完成后必须提醒用户配置

安装完成后，请明确提醒用户检查或编辑下面这些路径：

- 搜索凭据文件：`<search-skills path>/search-layer/search.json`
- 可选环境变量：`EXA_API_KEY`、`TAVILY_API_KEY`、`GROK_API_URL`、`GROK_API_KEY`、`GROK_MODEL`
- MinerU token 文件：`<search-skills path>/mineru-extract/.env`
- Workspace 环境变量：`SEARCH_SKILLS_WORKSPACE`

如果你无法确定 `<search-skills path>`，就告诉用户实际安装到了哪个本地目录，并基于那个真实路径给出配置文件位置。

### 安装完成后的最小回复要求

完成安装后，请向用户报告：

1. 实际安装了哪 3 个 skill
2. 每个 skill 的本地安装路径
3. 搜索配置文件路径
4. MinerU 配置文件路径
5. 如果 runtime 需要重启才能加载新 skill，提醒用户重启

## License

MIT
