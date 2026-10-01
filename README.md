# Supply Chain Incidences Catalogue

AI-generated catalogue of software supply-chain incidents.

**Live site:** https://ai-anant.github.io/supply-chain-incidences-catalogue/

## What is in here

- Incidents mapped to techniques
- Platforms (npm, PyPI, AI agents, MCP, and the rest)
- Conference talks, mapped only where the abstract matches a technique
- Sources the catalogue tracks
- Technique matrix

## Repository layout

- `content/oscar/techniques/` — techniques (`T####`)
- `content/oscar/mitigations/` — mitigations (`M####`)
- `content/oscar/detections/` — detections (`D####`)
- `content/oscar/stories/` — incident reconstructions mapped to techniques
- `content/portal/` — platforms, sources, talks, changelog
- `helpers/build_site.py` — static site generator (GitHub Pages)
- `helpers/validate_content.py` — YAML linter used in CI
- `docs/` — generated website (published to GitHub Pages)

## Local build

```bash
pip install -r requirements.txt
python helpers/validate_content.py
python helpers/build_site.py --dest docs
```

Open `docs/index.html`.

## License

Apache License 2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
