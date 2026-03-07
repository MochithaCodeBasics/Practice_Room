#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------------------------------------
# bundle‑artifact.sh
#
# Builds and bundles a Next.js project created by init‑artifact.sh into a
# single, self‑contained HTML file. The script runs the standard Next.js build
# process, exports the site to a static `out/` directory, and then uses
# `html-inline` to inline all linked CSS and JavaScript into one file.
#
# Usage: run from the root of your Next.js project after development:
#   bash ../scripts/bundle‑artifact.sh
#
##############################################################################

echo " Bundling Next.js app to single HTML artifact..."

# Ensure we are in a project directory
if [ ! -f "package.json" ]; then
  echo "❌ Error: package.json not found. Run this script from your project root."
  exit 1
fi

# Check that this is a Next.js project
if ! grep -q 'next' package.json; then
  echo "❌ Error: package.json does not reference Next.js. Did you run init‑artifact.sh?"
  exit 1
fi

# Install html-inline if not installed
if ! pnpm ls --depth=0 | grep -q html-inline >/dev/null 2>&1; then
  echo " Installing html-inline for bundling..."
  pnpm add -D html-inline
fi

# Build the Next.js app
echo " Building Next.js app..."
pnpm run build

# Export the site to static HTML (out/)
echo " Exporting static site..."
pnpm exec next export --outdir out

# Verify index.html exists
if [ ! -f "out/index.html" ]; then
  echo "❌ Error: Exported index.html not found in out/. Ensure your app has a page at '/'."
  exit 1
fi

# Inline all assets into single HTML
echo " Inlining all assets into a single HTML file..."
pnpm exec html-inline out/index.html > bundle.html

# Report file size
FILE_SIZE=$(du -h bundle.html | cut -f1)

echo ""
echo "✅ Bundle complete!"
echo " Output: bundle.html ($FILE_SIZE)"
echo ""
echo "You can now share this file directly in a Claude conversation."