# Supply Chain Incidences Catalogue

AI-generated catalogue of software supply-chain incidents. OSC&R is the technique framework inside it, not the whole project.

**Live site:** https://ai-anant.github.io/supply-chain-incidences-catalogue/

## What is in here

- Incidents mapped to techniques
- Platforms (npm, PyPI, AI agents, MCP, and the rest)
- Conference talks, mapped only where the abstract matches a technique
- Sources the catalogue tracks
- OSC&R, the technique matrix

## OSC&R, one part

OSC&R (Open Software Supply Chain Attack Reference) is the technique set: source control, CI/CD, artifacts, and the path into customer environments. That corpus was created by [pbom-dev/OSCAR](https://github.com/pbom-dev/OSCAR) under Apache-2.0. Principal original contributors include rubtoa, maxiozer, secvladimir, NaorPenso, vaq130, and 6mile. See [NOTICE](NOTICE). This catalogue does not claim that work, and it is not a continuation of OSCAR.

## Repository layout

- `content/oscar/techniques/` — OSC&R techniques (`T####`)
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

Apache License 2.0 — see [LICENSE](LICENSE).
