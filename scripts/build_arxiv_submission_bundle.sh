#!/usr/bin/env bash
set -euo pipefail

ROOT="/app"
ARTICLE_DIR="${ROOT}/docs/article-plans"
ASSET_DIR="${ARTICLE_DIR}/assets/2026-05-10_live-agent-risk"
OUT_DIR="${ARTICLE_DIR}/arxiv-submission"
BUNDLE_DIR="${OUT_DIR}/live-agent-risk-arxiv-source"

mkdir -p "${OUT_DIR}"
rm -rf "${BUNDLE_DIR}"
mkdir -p "${BUNDLE_DIR}/figures"

python3 - <<'PY'
from pathlib import Path

article_dir = Path("/app/docs/article-plans")
bundle_dir = article_dir / "arxiv-submission" / "live-agent-risk-arxiv-source"

tex = (article_dir / "2026-05-10_live-agent-risk-manuscript.tex").read_text()
tex = tex.replace(
    r"\graphicspath{{assets/2026-05-10_live-agent-risk/}}",
    r"\graphicspath{{figures/}}",
)
tex = tex.replace(
    r"\bibliography{2026-05-10_live-agent-risk-manuscript}",
    r"\bibliography{references}",
)

(bundle_dir / "main.tex").write_text(tex)
(bundle_dir / "references.bib").write_text(
    (article_dir / "2026-05-10_live-agent-risk-manuscript.bib").read_text()
)
PY

cp "${ASSET_DIR}"/fig*.pdf "${BUNDLE_DIR}/figures/"

cat > "${BUNDLE_DIR}/README.txt" <<'EOF'
arXiv submission source bundle for:

Evaluating LLMs as Live Strategic Agents:
Provider Ranking, Hybrid Decomposition, and Operational Gaps in Timed Risk Play

Main entry point: main.tex
Compiler: pdflatex

This bundle contains:
- main.tex
- references.bib
- references.bbl
- figures/*.pdf

Upload the contents of this directory, or upload the tar.gz package generated next to it.
EOF

# Verify the bundle compiles in isolation.
cd "${BUNDLE_DIR}"
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex >/dev/null

# Remove build byproducts from the upload directory.
rm -f main.aux main.blg main.fdb_latexmk main.fls main.log main.out main.pdf

cd "${OUT_DIR}"
tar -czf live-agent-risk-arxiv-source.tar.gz -C "${BUNDLE_DIR}" .

echo "Bundle directory: ${BUNDLE_DIR}"
echo "Bundle tarball: ${OUT_DIR}/live-agent-risk-arxiv-source.tar.gz"
