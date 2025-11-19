---
name: web-access
description: Search the web and fetch page content
---

# web-access

## 🎯 Triggers
**When user wants to:**
- Search the internet
- Get current/recent information
- Fetch content from a URL
- Access online documentation

**Skip when:**
- Answer is within knowledge cutoff
- Local file operation

## Scripts

### search
**What:** Search the web using Brave Search API
**Pattern:** User wants to search → `script_run web-access search --query "USER_QUERY" --json`
**Example:** "Search for python tutorials" → `script_run web-access search --query "python tutorials" --json`

### fetch
**What:** Fetch and convert web page to markdown
**Pattern:** User provides URL → `script_run web-access fetch --url "USER_URL" --json`
**Example:** "Get https://example.com" → `script_run web-access fetch --url "https://example.com" --json`

## Quick Reference
```
User: "Search for X"          → script_run web-access search --query "X" --json
User: "Fetch https://..."     → script_run web-access fetch --url "https://..." --json
User: "Find recent news on X" → script_run web-access search --query "X news" --json
```

## Requires
- `BRAVE_API_KEY` environment variable for search
