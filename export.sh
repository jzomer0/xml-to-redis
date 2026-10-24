#!/usr/bin/env bash
set -euo pipefail

VERBOSE=""
[ "${1:-}" = "-v" ] && { VERBOSE="-v"; shift; }
[ $# -eq 1 ] || { echo "Usage: ./export.sh [-v] /path/to/xml" >&2; exit 2; }
[ -f "$1" ] || { echo "File not found: $1" >&2; exit 1; }

XML_ABS="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"

cd "$(dirname "${BASH_SOURCE[0]}")"
docker compose run --rm --build -v "$XML_ABS:/data/config.xml:ro" app $VERBOSE /data/config.xml
