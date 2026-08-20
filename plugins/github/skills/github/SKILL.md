---
name: github
description: GitHub operations via the gh CLI — create and publish repos, change visibility, pull-request workflow, releases, issues. Use when the user says "create a repo", "publish", "push to github", "release", "open a PR", "create an issue", "make the repo private/public", or needs GitHub management beyond plain git push.
---

# GitHub Operations

Everything runs through the **gh CLI** — it uses the logged-in user's token and can therefore do what scoped app integrations often cannot: create repos, change visibility, publish releases.

## Always first: check availability

```bash
gh auth status
```

- **OK** → continue with the recipes below.
- **`gh` missing or not logged in** → tell the user exactly that, with the fix: `gh auth login` or installation (https://cli.github.com). Don't guess, don't keep trying with half the permissions.
- **Remote environment with a GitHub App instead of gh** (Claude Code Web/Remote): the app scope typically **cannot create repos or change visibility** (403 "Resource not accessible by integration"). In that case: prepare everything (files, structure, commits), tell the user the 1–2 manual steps on github.com, push once they confirm.

## Create & publish a repo

New repo from an existing directory:

```bash
gh repo create <name> --private --source . --push
```

- `--private` is this skill's default. **`--public` only when the user has explicitly asked to publish** — and then confirm in one line what becomes public before running the command.
- Before any first push to a public repo: check for secrets (`.env`, keys, tokens in history). Found something → stop and report, do not push.
- Empty repo with no local code: `gh repo create <name> --private --clone`.

Change visibility:

```bash
gh repo edit <owner>/<repo> --visibility public --accept-visibility-change-consequences
```

Public→private breaks third parties' existing clones/installations — state the risk in one line first, wait for confirmation.

## Pull-request workflow

```bash
git checkout -b <branch> && git push -u origin <branch>
gh pr create --draft --title "..." --body "..."
gh pr merge <nr> --squash --delete-branch
```

- Open PRs as drafts unless the user wants to merge straight away.
- PR description: what and why, normal prose — it's documentation for other people.
- Respect the repo's PR template (`.github/pull_request_template.md`) when present.

## Releases

```bash
gh release create v<version> --title "v<version>" --notes "..."
```

Read the version from the project (`package.json`, `plugin.json`, tags) — don't invent it. Notes: changes since the last release, from `git log <lasttag>..HEAD`.

## Issues

```bash
gh issue create --title "..." --body "..."
gh issue list --state open
```

Check for duplicates with `gh issue list --search "..."` before creating.

## Security rules (non-negotiable)

- **Never without an explicit user instruction:** delete/archive a repo, make it public, force-push to shared branches, delete releases.
- `gh repo delete` only after literal confirmation naming the repo, from the user.
- Never write tokens/secrets into commands, logs, or commits.
- On 403/404 against existing repos: report the permissions problem first (app scope? login?), don't blindly retry.
