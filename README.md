# AI Agent Project Template

> **Stop configuring. Start building.** Production-ready scaffolding for AI-assisted development.

[![MCP Ready](https://img.shields.io/badge/MCP-Ready-blueviolet)]()
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)]()
[![MIT License](https://img.shields.io/badge/License-MIT-green)]()

---

## The Problem

You fire up Claude Code on a new project. It's brilliant... until it forgets your preferences. Again. You explain your stack. Again. You watch it reinvent patterns you've already solved. *Again.*

Sound familiar? Yeah, we've been there too.

---

## The Solution

This template gives your AI assistant something it desperately needs: **memory, context, and structure**.

Think of it as onboarding documentation for your silicon colleague. Instead of starting from scratch every session, your AI reads the project files and *actually remembers* how you like things done.

**What's inside:**

| Component | What It Does | Why You'll Love It |
|-----------|--------------|-------------------|
| 🧠 **Persistent Memory** | Notes that survive across sessions | No more "as I mentioned earlier..." |
| 🔍 **Web Search** | Brave, Google, Context7 built-in | Research without leaving your IDE |
| 📋 **Workflow Templates** | Pre-built patterns for common tasks | Data analysis, research, creative writing |
| 🗄️ **SQLite Integration** | Query-first patterns for big data | Stop feeding 10K rows to the context window |
| 📁 **Context System** | Session state that persists | Pick up exactly where you left off |

---

## Who Is This For?

- **Solo developers** who pair-program with AI daily
- **Teams** who want consistent AI behavior across projects
- **Anyone** tired of re-explaining their project structure to a forgetful robot

---

## Quick Taste

```bash
# Clone it
git clone https://github.com/your-username/ai-project-template
cd ai-project-template

# Set it up (details in HOWTO.md)
conda create -n ai-project python=3.11 && conda activate ai-project
pip install -r requirements.txt

# ⭐ THE STEPS YOUR AI IS BEGGING YOU NOT TO SKIP ⭐
python tools/sync_rules.py --ide cline   # Teach your AI to read
python tools/setup_mcp.py --check        # Give your AI superpowers

# Configure your API keys
cp api-keys.json api-keys.local.json

# Watch your AI actually understand your project
```

> 🤖 **Plot twist:** Your AI assistant can't read minds, but it *can* read `.clinerules`. Skip the sync step and watch it confidently do everything wrong. We've all been there. Don't be a hero—run the scripts.

For the full setup walkthrough (including why those first two steps matter), head to **[HOWTO.md](./HOWTO.md)**.

---

## What Makes This Different?

### 1. The `.agent/` Folder

Your AI's home base. Contains:
- **context/** — Current focus, known issues, recent changes
- **workflows/** — Reusable playbooks for research, analysis, writing
- **docs/** — Architecture decisions that don't change often

### 2. The `AGENTS.md` File

The constitution for your AI assistant. Coding conventions, project quirks, "please don't do X" warnings—all in one place. Your AI reads this automatically.

### 3. Actually Useful MCP Servers

Pre-configured integrations that extend what your AI can do:
- **Pomera** — 22 text processing tools + persistent notes
- **Sequential Thinking** — Structured problem-solving with revision
- **Text Editor** — Hash-based conflict detection for safe edits

---

## The Workflows

We've included battle-tested patterns for:

- **🔬 Research Projects** — Multi-engine search, source triangulation, synthesis
- **📊 Data Analysis** — SQLite-first patterns, query before reasoning
- **✍️ Creative Writing** — Drafting, revision tracking, word frequency analysis
- **💻 Coding Sessions** — State saving, incremental validation, clean commits

Each workflow is documented in `.agent/workflows/` and ready to use.

---

## 🎯 Master Your Prompts, Save Tokens

> **Prompts are code.** Treat them like it—version them, test them, iterate.

This template includes a **Prompt Progression Guide** (`.agent/docs/prompt-progression-guide.md`) that teaches you to systematically improve your AI interactions.

### Why It Matters

| Without System | With Prompt System |
|----------------|-------------------|
| ❌ Repeat same mistakes | ✅ Learn from every prompt |
| ❌ Waste tokens on vague requests | ✅ Precise, efficient prompts |
| ❌ Inconsistent results | ✅ Reproducible quality |
| ❌ Re-invent the wheel | ✅ Reusable prompt library |

### Token Savings You Can Achieve

| Technique | Potential Savings |
|-----------|-------------------|
| Explicit output format | 20-30% fewer re-prompts |
| Few-shot examples | 30-50% less iteration |
| Constraints & boundaries | 20-40% shorter responses |
| Prompt caching (static context first) | Up to 90% on repeated calls |
| RAG (inject only relevant docs) | Up to 70% context reduction |

### The Progression Path

| Level | Focus | Key Skill |
|-------|-------|-----------|
| **Beginner** | Clear commands | Explicit formatting |
| **Intermediate** | Structured thinking | POWER framework + few-shot |
| **Advanced** | Meta-cognition | Self-improvement patterns |
| **Expert** | Context engineering | Autonomous agent design |

**👉 Start here:** Read [`.agent/docs/prompt-progression-guide.md`](./.agent/docs/prompt-progression-guide.md) and pick ONE technique to practice this week.

---

## Getting Started

1. **Read the README** (you're doing great so far 👍)
2. **Follow [HOWTO.md](./HOWTO.md)** for complete setup instructions
3. **Customize `AGENTS.md`** for your project's specific needs
4. **Add your workflows** to `.agent/workflows/` as you develop patterns

---

## Project Structure (The Short Version)

```
ai-project-template/
├── .agent/              # Your AI's brain
│   ├── context/         # Session state
│   ├── docs/            # Architecture
│   └── workflows/       # Reusable patterns
├── tools/               # Python utilities
│   ├── web_search.py    # Multi-engine search
│   └── email/           # Example: email processing
├── AGENTS.md            # AI constitution
├── HOWTO.md             # Setup guide
└── README.md            # You are here
```

---

## FAQ

**Q: Does this work with Claude Code only?**  
A: It's optimized for Claude Code, but the patterns work with any AI that can read markdown files. See our [rule-mapping workflow](./.agent/workflows/rule-mapping.md) for syncing to other IDEs.

**Q: Is this overkill for small projects?**  
A: Maybe! But once you've experienced AI that *remembers*, you won't go back.

**Q: Can I use this commercially?**  
A: Absolutely. MIT license. Go wild.

---

## Contributing

Found a bug? Have a workflow to share? PRs welcome!

---

## License

MIT — See [LICENSE](./LICENSE) for details.

---

<p align="center">
  <i>Built with ☕ and occasional frustration at forgetful AI assistants.</i>
</p>
