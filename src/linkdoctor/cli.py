from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import analyze
from .render import write_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose Azure Private Link evidence without changing Azure")
    parser.add_argument("bundle", help="Evidence bundle JSON")
    parser.add_argument("--output", default="generated/linkdoctor")
    parser.add_argument("--fail-on-diagnosis", action="store_true")
    args = parser.parse_args()
    bundle = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
    report = analyze(bundle)
    paths = write_outputs(bundle, report, args.output)
    print(json.dumps({"status": report["status"], "root_causes": report["summary"]["root_causes"],
                      "outputs": {key: str(path) for key, path in paths.items()}}, indent=2))
    if report["status"] == "INCOMPLETE" or (args.fail_on_diagnosis and report["findings"]):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
