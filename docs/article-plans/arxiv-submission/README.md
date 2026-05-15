# arXiv Submission Kit

This folder contains a clean arXiv upload bundle plus the metadata and checklist needed to submit the paper.

## Files

- `live-agent-risk-arxiv-source/`
  - clean LaTeX upload directory
- `live-agent-risk-arxiv-source.tar.gz`
  - ready-to-upload arXiv source tarball
- `metadata_draft.md`
  - title, abstract, comments, category, and license recommendation
- `submission_checklist.md`
  - final pre-submission checklist

## Relevant arXiv help pages

- Endorsement: `https://info.arxiv.org/help/endorsement.html`
- Metadata preparation: `https://info.arxiv.org/help/prep.html`
- TeX Live / LaTeX environment: `https://info.arxiv.org/help/faq/texlive.html`
- License help: `https://arxiv.org/help/license`

## How the bundle was prepared

The bundle is derived from:

- `docs/article-plans/2026-05-10_live-agent-risk-manuscript.tex`
- `docs/article-plans/2026-05-10_live-agent-risk-manuscript.bib`
- `docs/article-plans/assets/2026-05-10_live-agent-risk/`

It rewrites the manuscript to a cleaner arXiv layout:

- `main.tex` as the entry point
- `figures/` as the figure directory
- `references.bib` and `references.bbl` as the bibliography files

## Rebuild command

Run inside the project container:

```bash
bash scripts/build_arxiv_submission_bundle.sh
```
