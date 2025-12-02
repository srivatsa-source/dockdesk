# 🛡️ DockDesk

**Stop lying to your team.**
DockDesk is an AI-powered GitHub Action that prevents "Knowledge Rot." It scans your Pull Requests and blocks the merge if your code logic contradicts your documentation.

## 🚀 Usage

Add this to your `.github/workflows/dockdesk.yml` file:

```yaml
name: DockDesk Audit

on: [pull_request]

jobs:
  audit_docs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Run DockDesk
        uses: your-github-username/dockdesk@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          code_file: 'src/server.js'     # The code you want to check
          doc_file: 'docs/api.md'        # The docs that should match