# 🛡️ DockDesk

<div align="center">

<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1000&color=2786F7&center=true&vCenter=true&width=500&lines=Stop+drifting.;Stop+lying+to+your+team.;AI-powered+documentation+auditing." alt="Typing SVG" />
</a>

> **The AI Auditor that ensures your Code never contradicts your Documentation.**

<p align="center">
  <a href="#-see-it-in-action">View Demo</a> •
  <a href="#-setup">Installation</a> •
  <a href="#-how-it-works">How It Works</a>
</p>

<p align="center">
<img src="https://img.shields.io/badge/AI%20Model-Gemini%202.0%20Flash-8E74F1?style=for-the-badge&logo=google&logoColor=white" alt="AI Model">
<img src="https://img.shields.io/github/actions/workflow/status/srivatsa-source/dockdesk/main.yml?style=for-the-badge&label=BUILD" alt="Build Status">
<img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License">
</p>

</div>

---

## 🎥 See it in Action

Docs say one thing. Code does another. **DockDesk catches it before you merge.**

<div align="center">
  <img src="demo.gif" alt="DockDesk Demo Animation" width="800" style="border-radius: 10px; box-shadow: 0px 0px 20px rgba(0,0,0,0.2);">
</div>

---

## 💀 The Problem: "Knowledge Drift"

Developers write code faster than they write documentation.

1. ❌ Code gets updated  
2. ❌ Docs remain outdated  
3. 🔥 **Result:** API consumers suffer, onboarding slows, confusion spreads

---

## ⚡ The Solution: Active Compliance

DockDesk is not a keyword-based static analyzer.  
It's an AI auditor that understands **context and intent**.

It lives in your CI/CD pipeline and audits every Pull Request using **Gemini 2.0**.

| Feature | Description |
|--------|-------------|
| 👀 **Reads** | Scans updated code and documentation. |
| 🧠 **Thinks** | Detects contradictions like “public” vs “admin-only”. |
| 🗣️ **Speaks** | Blocks the PR & comments what must be fixed. |

---

## 🧠 How It Works: The "Knowledge Integrity" Architecture

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#2786F7', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#f4f4f4'}}}%%
graph TD
    subgraph PERCEPTION ["👁️ PERCEPTION LAYER"]
        A([💻 Dev Pushes Code]) -->|Pull Request| B(GitHub Action)
        B -->|Identify Changed Files| C{tj-actions/changed-files}
    end

    subgraph REASONING ["🧠 REASONING LAYER"]
        C -->|Code + Docs| D[Integrity Agent]
        D -->|Context & Intent| E[Gemini 2.0 Flash]
        E -->|Semantic Analysis| F{Contradiction?}
    end

    subgraph ACTION ["🛡️ ACTION LAYER"]
        F -- YES --> G[❌ Block PR]
        G --> H[📝 Post Audit Report]
        G --> I[🔌 Slack Alert (Enterprise)]
        F -- NO --> J[✅ Pass Checks]
    end

    style A fill:#2196F3,stroke:#fff,stroke-width:2px,color:#fff
    style E fill:#8E74F1,stroke:#fff,stroke-width:2px,color:#fff
    style G fill:#F44336,stroke:#fff,stroke-width:2px,color:#fff
    style J fill:#4CAF50,stroke:#fff,stroke-width:2px,color:#fff
```

## 📦 Setup

Create this file:

.github/workflows/dockdesk.yml


And paste:

name: DockDesk Audit
on: [pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write # Required for commenting
    steps:
      - uses: actions/checkout@v3

      - name: Run AI Auditor
        uses: srivatsa-source/dockdesk@main
        with:
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}

          # Files to compare
          code_file: 'src/auth.js'
          doc_file: 'docs/API.md'

## 🛠️ Interactive Mode & Agentic Workflow

DockDesk is designed to be the **Verification Layer** for both human developers and AI Agents. It prevents "Knowledge Decay" by ensuring documentation is always the Source of Truth.

### 🧑‍💻 For Developers (Interactive Fix)

Run DockDesk locally to verify your changes before pushing. If a contradiction is found, DockDesk can **automatically fix your documentation**.

```bash
python sauce.py src/my_feature.py docs/feature_specs.md
```

**Output:**
```text
🚨 DRIFT DETECTED!
Reason: Code implements 'guest' access, but docs specify 'admin-only'.
Suggestion: Update docs to reflect guest access.

🤖 DockDesk can automatically fix the documentation.
Do you want to overwrite 'docs/feature_specs.md' with the fixed version? [y/N]: y
✅ Documentation updated successfully!
```

### 🤖 For AI Agents (JSON Mode)

Agents can invoke `sauce.py` with the `--json` flag to get machine-readable output. This allows agents to self-correct and verify their own code generation against existing documentation.

```bash
python sauce.py src/my_feature.py docs/feature_specs.md --json
```

**Output:**

```json
{
  "has_contradiction": true,
  "reason": "Code implements 'guest' access, but docs specify 'admin-only'.",
  "suggested_fix_description": "Update docs to reflect guest access.",
  "new_doc_content": "# Feature Specs\n\n..."
}
```

<div align="center"> Built by Vatsa </div>

---

## 🛠️ Utilities

### `list_models.py`
A simple script to list available Gemini models.
- **Auth:** Requires the `GEMINI_API_KEY` environment variable to be set to `admin_secret`.
- **Usage:** `python list_models.py` ```