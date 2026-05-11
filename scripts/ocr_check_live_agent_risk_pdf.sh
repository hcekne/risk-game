#!/usr/bin/env bash
set -euo pipefail

PDF="/app/docs/article-plans/2026-05-10_live-agent-risk-manuscript-latex.pdf"
OUTDIR="/app/docs/article-plans/ocr/2026-05-10_live-agent-risk"
SEARCH_CMD="grep -En"

if command -v rg >/dev/null 2>&1; then
  SEARCH_CMD="rg -n"
fi

mkdir -p "$OUTDIR"

pdftoppm -png -r 180 "$PDF" "$OUTDIR/page"

rm -f "$OUTDIR"/ocr_summary.txt

for img in "$OUTDIR"/page-*.png; do
  base="$(basename "$img" .png)"
  tesseract "$img" "$OUTDIR/$base" >/dev/null 2>&1
done

cat "$OUTDIR"/page-*.txt > "$OUTDIR"/all_pages_ocr.txt

{
  echo "PDF: $PDF"
  echo "Pages rendered to: $OUTDIR"
  echo
  echo "Title matches:"
  $SEARCH_CMD "Evaluating LLMs as Live Strategic Agents" "$OUTDIR"/all_pages_ocr.txt || true
  echo
  echo "Section matches:"
  $SEARCH_CMD "Introduction|Related Work|Experimental Harness|Conclusion|References" "$OUTDIR"/all_pages_ocr.txt || true
  echo
  echo "Figure matches:"
  $SEARCH_CMD "Figure 1|Figure 2|Figure 3|Figure 4|Figure 5|Figure 6|Figure 7" "$OUTDIR"/all_pages_ocr.txt || true
} > "$OUTDIR/ocr_summary.txt"

cat "$OUTDIR/ocr_summary.txt"
