from __future__ import annotations

import argparse
import json
from pathlib import Path

from manifest_core import ManifestError, prepare_manifest, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one social publish manifest.")
    parser.add_argument("manifest")
    parser.add_argument("--json-out")
    args = parser.parse_args()
    try:
        prepared = prepare_manifest(args.manifest)
    except ManifestError as exc:
        print(json.dumps({"status": "preflight-failed", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    if args.json_out:
        write_json(Path(args.json_out).expanduser().resolve(), prepared.report)
    print(json.dumps(prepared.report, ensure_ascii=False, indent=2))
    return 0 if prepared.report["status"] == "preflight-passed" else 3


if __name__ == "__main__":
    raise SystemExit(main())
