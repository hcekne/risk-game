#!/usr/bin/env bash
set -euo pipefail

cd /app/docs/article-plans

latexmk -pdf -interaction=nonstopmode -halt-on-error 2026-05-10_live-agent-risk-manuscript.tex

cp 2026-05-10_live-agent-risk-manuscript.pdf 2026-05-10_live-agent-risk-manuscript-latex.pdf
