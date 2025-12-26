# 🎬 DockDesk: The "Golden Demo" Script
**Target Audience:** Atomicwork CEO & Leadership Team
**Goal:** Demonstrate "Knowledge Integrity" and "Self-Healing Documentation."

---

## 1. The Setup (1 Minute)
**Say:**
> "We all know the pain of 'Documentation Drift.' An engineer updates the code, forgets the docs, and suddenly your internal AI bot is giving wrong answers to employees.
> Today, I'm showing you **DockDesk**. It's not just a linter; it's a **Knowledge Integrity Agent** that lives in your pipeline."

---

## 2. The "Drift" (The Action)
**Action:**
1. Open `list_models.py` in VS Code.
2. Change a line to introduce a logic conflict.
   * *Example:* Change `if not api_key:` to `if api_key == "admin_secret":` (Simulating a sudden auth change).
3. Commit and Push to a new branch.
4. Open a Pull Request.

**Say:**
> "I'm simulating a common scenario. I just changed the authentication logic to require a specific secret, but I 'forgot' to update the README. Normally, this would merge silently."

---

## 3. The "Perception & Reasoning" (The Wait)
**Action:**
1. Show the GitHub Action running.
2. Click into the "Semantic Audit" job.

**Say:**
> "Right now, DockDesk's **Perception Layer** has identified the changed files. It's passing them to the **Reasoning Layer**, powered by Gemini 2.0. It's reading the code *and* the docs, looking for semantic contradictions, not just syntax errors."

---

## 4. The "Gatekeeping" (The Reveal)
**Action:**
1. The Workflow FAILS (Red X).
2. Scroll down to the PR Comment.

**Say:**
> "And here is the magic. The PR is blocked. But look at the report."

**Highlight:**
1. **Risk Score:** "It flagged this as **High Risk** because it involves 'Auth'."
2. **Enterprise Integration:** "It generated a webhook payload for Slack/Teams, so the Engineering Manager gets alerted immediately."

---

## 5. The "Self-Healing" (The Wow Moment)
**Action:**
1. Expand the **"✨ View Self-Healed Documentation"** dropdown in the comment.

**Say:**
> "But we don't just block; we fix. The agent has already rewritten the documentation to match the new code reality. I can just copy this, commit it, and the knowledge gap is closed instantly."

---

## 6. Closing
**Say:**
> "This is how we ensure Atomicwork's AI always has the truth. We stop drift at the source."
