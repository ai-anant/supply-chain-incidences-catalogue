<!-- TOWNCRIER -->

# v0.3.0 (2026-09-21)

Public portal changelog, guidance gap-fill, technique provenance.

## Features

* Site pages: `/changelog.html`, `/guidance.html`
* T0206 forge/omit provenance, T0207 skip/forge integrity, T0208 compromise code-signing
* AS23 repo jacking (Security Innovation), AS24 self-hosted runners (Praetorian Gato)
* Technique pages distinguish observed-in-incidents vs identified-from-research

# v0.2.0 (2026-09-21)

First public site, including the OSC&R corpus from pbom-dev/OSCAR.

## Features

* GitHub Pages site: matrix, technique pages, incident → OSC&R mapping
* New techniques T0200–T0203, T0205 from upstream issues and incident gaps
* New attack stories AS7–AS22
* Content linter (`helpers/validate_content.py`)

## Bugfixes

* Applied unmerged upstream PRs #113, #114, #115
* D1171 typed as Detection (issue #108)
* T0176 wording covers disablement of controls (issue #22)
* matrix.json now records `amount` and technique `id` (issue #41)

## Miscellaneous

* NOTICE and README record OSC&R attribution. The catalogue is not a continuation of OSCAR.
* CONTRIBUTING.md rewritten (issues #10, #12)

# v0.0.1 (2023-02-11)

## Features

* Initial content and structure creation for the OSC&R repository
