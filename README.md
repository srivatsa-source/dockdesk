# 🛡️ DockDesk

> **Stop lying to your team.**
> The AI Auditor that ensures your Code never drifts from your Documentation.

[![GitHub Actions](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/srivatsa-source/dockdesk)
[![AI Powered](https://img.shields.io/badge/AI-Gemini%202.0-blue)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎥 See it in Action
![DockDesk Demo](demo.gif)
*(The bot detects that the code requires Admin access, but the docs say "Public". It blocks the merge and suggests a fix.)*

---

## 💀 The Problem: "Knowledge Drift"
Developers write code faster than they write documentation.
1.  You update the API to require `Auth`.
2.  You forget to update the `README`.
3.  **Result:** Your team wastes hours debugging, and your customers get frustrated.

## ⚡ The Solution: Active Compliance
**DockDesk** is not a passive writer. It is an active **Sheriff**.
It sits in your CI/CD pipeline and audits every Pull Request.
* **👀 Reads:** Scans your logic changes (`.js`, `.py`, etc.) and your docs (`.md`).
* **🧠 Thinks:** Uses **Google Gemini 2.0** to detect semantic contradictions (not just keywords).
* **🗣️ Speaks:** Comments directly on the PR with the exact fix required.

---

## 🚀 Installation
Add this to your `.github/workflows/audit.yml`:

```yaml
name: DockDesk Audit
on: [pull_request]

jobs:
  check-docs:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write # Required to post comments
    steps:
      - uses: actions/checkout@v3
      - name: Run DockDesk
        uses: srivatsa-source/dockdesk@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }} # Supports Gemini Keys too!
          github_token: ${{ secrets.GITHUB_TOKEN }}
          code_file: 'src/auth.js'  # The code you want to watch
          doc_file: 'docs/api.md'   # The source of truth