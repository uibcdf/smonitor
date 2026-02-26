#!/usr/bin/env bash
echo "Building"
set -ex

$PYTHON -m pip install . --no-deps -v
echo "Done"
