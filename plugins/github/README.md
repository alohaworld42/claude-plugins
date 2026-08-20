# github

GitHub management via the gh CLI — for everything `git push` alone can't do.

## Purpose

Scoped app integrations (e.g. Claude Code Remote) often can't create repos or change visibility. The gh CLI with a user login can. This skill gives Claude the recipes and — more importantly — the guardrails:

- **Create & publish repos** (`gh repo create`), private by default, public only on explicit request with confirmation
- **Change visibility** with a risk note (public→private breaks other people's clones/installations)
- **PR workflow** (draft PRs, squash merge, branch cleanup)
- **Releases & issues** (read versions from the project, duplicate check)
- **Secret check** before the first push to a public repo

Without the gh CLI (remote environment with app scope) the skill prepares everything and tells the user the 1–2 manual steps, instead of failing on 403 errors.

## Installation

```
/plugin install github@alohaworld-plugins
```

Requires the [gh CLI](https://cli.github.com) installed and logged in (`gh auth login`).
