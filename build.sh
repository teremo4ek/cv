#!/usr/bin/env bash
set -euo pipefail

TEX_FILE="${1:-yury_bely_cv.tex}"
OUT_DIR="${2:-output}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BASENAME=$(basename "$TEX_FILE" .tex)

mkdir -p "$OUT_DIR"

docker run --rm \
  -v "$(pwd)":/workspace \
  -w /workspace \
  texlive/texlive \
  pdflatex -interaction=nonstopmode -output-directory="$OUT_DIR" "$TEX_FILE"

# Clean up everything except the PDF, then rename with timestamp
cd "$OUT_DIR"
rm -f "${BASENAME}.aux" "${BASENAME}.log" "${BASENAME}.out"
mv "${BASENAME}.pdf" "${BASENAME}_${TIMESTAMP}.pdf"
