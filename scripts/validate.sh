#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src python3 -m unittest discover -s tests -v

output_root="${TMPDIR:-/tmp}/linkdoctor-validation"
rm -rf "$output_root"

for bundle in examples/*.json; do
  scenario="$(basename "$bundle" .json)"
  set +e
  PYTHONPATH=src python3 -m linkdoctor.cli "$bundle" --output "$output_root/$scenario" --fail-on-diagnosis
  status=$?
  set -e
  if [[ "$status" -ne 2 ]]; then
    echo "Expected diagnosed fixture $bundle to exit 2; got $status" >&2
    exit 1
  fi
  test -s "$output_root/$scenario/diagnosis.json"
  test -s "$output_root/$scenario/support-bundle.zip"
done
