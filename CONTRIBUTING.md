# Contributing to the Supply Chain Incidences Catalogue

This catalogue is AI-generated. OSC&R is the technique framework inside it, not the whole project. Original OSC&R authors retain credit for that corpus; see [NOTICE](NOTICE).

## How to contribute

1. Open an issue first (bug, new technique, new incident mapping, or docs).
2. Fork this repo and branch from `main`.
3. One pull request per issue; reference the issue in the PR body (`Fixes #N`).
4. PRs target `main`. Releases are tags, not long-lived branches.
5. Content lives in YAML under `content/oscar/`. Follow `content/templates/`.
6. Run the linter before you open the PR:

```bash
pip install -r requirements.txt
python helpers/validate_content.py
python helpers/build_site.py --dest docs
```

7. Technique IDs are `T####` and must be unique. If you are unsure of the next ID, say so in the issue.

## Content rules

- Required technique fields: `id`, `type`, `tactic`, `realm`, `summary`, `description`
- `tactic` must be one of the 12 OSC&R tactics (same names as MITRE ATT&CK)
- Link mitigations (`M####`) and detections (`D####`) by ID; create those YAML files in the same PR if they do not exist
- Attack stories go in `content/oscar/stories/` and must map at least one existing technique
- Prefer adding a `gaps:` list on stories when the framework cannot yet name an element

## Project management

- Issues and pull requests on GitHub are the system of record
- Use GitHub Discussions when they are enabled
- The original Slack (`osc-r.slack.com`) may no longer be active; prefer GitHub
