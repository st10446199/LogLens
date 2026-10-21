"""Command line entry point: python -m loglens input.log [output] [exact|normalized]."""
import json
from pathlib import Path
import sys
from .core import analyze
from .report import html_report

def main(args=None):
    args = sys.argv[1:] if args is None else args
    if not 1 <= len(args) <= 3 or (len(args) == 3 and args[2] not in {"exact", "normalized"}):
        print("Usage: python -m loglens input.log [output directory] [exact|normalized]", file=sys.stderr)
        return 2
    source = Path(args[0])
    output = Path(args[1]) if len(args) >= 2 else Path("reports")
    try:
        if source.stat().st_size > 50 * 1024 * 1024:
            raise ValueError("Input exceeds 50 MiB. Split the log into smaller files.")
        if source.resolve() in {(output / name).resolve() for name in ("report.html", "summary.json")}:
            raise ValueError("Output would overwrite the input file. Choose another directory.")
        with source.open(encoding="utf-8") as stream:
            result = analyze(stream, normalize=len(args) == 3 and args[2] == "normalized")
        output.mkdir(parents=True, exist_ok=True)
        (output / "report.html").write_text(html_report(result, source.name), encoding="utf-8")
        (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"Parsed {result['total']} records; {result['errors']} errors; {result['skipped']} skipped.")
        print(f"Report: {(output / 'report.html').resolve()}")
        return 0 if result["total"] else 1
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Cannot analyze log: {error}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
