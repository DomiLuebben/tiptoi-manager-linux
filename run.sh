#!/usr/bin/env bash
# Runner script for tiptoi® Manager Linux
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

python3 main.py "$@"
