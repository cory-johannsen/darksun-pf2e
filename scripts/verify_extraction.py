"""Compare legacy vs structured extraction outputs with HTML previews."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional


def _add_repo_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_feedback(path: Optional[Path]) -> Dict[str, dict]:
    if path is None:
        return {}
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "PyYAML is required to read YAML feedback files. Install it or provide JSON."
            ) from exc
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    else:
        data = _load_json(path)
    if not isinstance(data, dict):
        raise ValueError("Feedback file must contain an object mapping slugs to configuration overrides")
    return data


def _find_section(raw_dir: Path, slug: str) -> Optional[Path]:
    matches = sorted(raw_dir.glob(f"*-{slug}.json"))
    if matches:
        return matches[0]
    return None


def _render_diff(title: str, structured_html: str, legacy_html: str) -> str:
    diff = difflib.HtmlDiff(wrapcolumn=80)
    structured_lines = structured_html.splitlines()
    legacy_lines = legacy_html.splitlines()
    table = diff.make_table(structured_lines, legacy_lines, context=True, numlines=2)
    return f"<section class=\"diff\"><h2>Diff: {title}</h2>{table}</section>"


def _build_preview_html(
    slug: str,
    structured_html: str,
    legacy_html: str | None,
    notes: str | None = None,
    diff_enabled: bool = True,
) -> str:
    diff_block = ""
    if diff_enabled and legacy_html is not None:
        diff_block = _render_diff(slug, structured_html, legacy_html)

    notes_block = f"<section class=\"notes\"><h2>Reviewer Notes</h2><p>{notes}</p></section>" if notes else ""

    legacy_panel = (
        f"<article><h2>Legacy</h2><div class=\"preview legacy\">{legacy_html}</div></article>"
        if legacy_html is not None
        else ""
    )

    return (
        "<html><head>"
        "<meta charset=\"utf-8\"/>"
        "<style>body{font-family:Inter,Helvetica,Arial,sans-serif;margin:2rem;}"
        ".panels{display:grid;gap:2rem;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));}"
        ".preview{border:1px solid #ccc;padding:1rem;min-height:200px;background:#fff;}"
        ".preview table{border-collapse:collapse;width:100%;}"
        ".preview td{border:1px solid #ddd;padding:0.5rem;vertical-align:top;}"
        "table.diff{width:100%;overflow:auto;}"
        "</style></head><body>"
        f"<h1>{slug}</h1>"
        f"<section class=\"panels\">"
        f"<article><h2>Structured</h2><div class=\"preview structured\">{structured_html}</div></article>"
        f"{legacy_panel}"
        f"</section>"
        f"{diff_block}"
        f"{notes_block}"
        "</body></html>"
    )


def _render_with_transformer(transformer_key: str, payload: dict, config: dict | None = None) -> str:
    from tools.pdf_pipeline.transformers import REGISTRY

    transformer = REGISTRY.get(transformer_key)
    if transformer is None:
        raise KeyError(f"Unknown transformer '{transformer_key}'")
    result = transformer(payload, config or {})
    return result.get("content", "")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", action="append", help="Specific slug(s) to preview. Can be passed multiple times.")
    parser.add_argument(
        "--glob",
        default=None,
        help="Glob pattern to select structured section files when slug is not provided.",
    )
    parser.add_argument(
        "--structured-dir",
        type=Path,
        default=Path("data/raw_structured/sections"),
        help="Directory containing structured extraction JSON files.",
    )
    parser.add_argument(
        "--legacy-dir",
        type=Path,
        default=Path("data/raw/sections"),
        help="Directory containing legacy extraction JSON files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/verification"),
        help="Directory where HTML preview files will be written.",
    )
    parser.add_argument(
        "--feedback",
        type=Path,
        default=None,
        help="Optional JSON/YAML file providing transformer overrides and reviewer notes.",
    )
    parser.add_argument(
        "--transformer",
        default="journal",
        help="Transformer key to render structured sections (default: journal).",
    )
    parser.add_argument(
        "--legacy-transformer",
        default="journal",
        help="Transformer key to render legacy sections for comparison.",
    )
    parser.add_argument(
        "--no-diff",
        action="store_true",
        help="Skip generating HTML diff output for faster preview generation.",
    )
    return parser.parse_args()


def main() -> None:
    _add_repo_path()

    args = parse_args()
    feedback = _load_feedback(args.feedback)

    if not args.structured_dir.exists():
        raise FileNotFoundError(f"Structured directory not found: {args.structured_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.slug:
        slugs: Iterable[str] = args.slug
    else:
        pattern = args.glob or "*.json"
        slugs = [path.name.split("-", maxsplit=2)[-1].rsplit(".json", 1)[0] for path in args.structured_dir.glob(pattern)]

    written: List[Path] = []
    for slug in slugs:
        structured_path = _find_section(args.structured_dir, slug)
        if structured_path is None:
            print(f"Skipping '{slug}': structured file not found", file=sys.stderr)
            continue

        structured_data = _load_json(structured_path)
        structured_config = feedback.get(slug, {}).get("transformer_config", {})
        structured_html = _render_with_transformer(args.transformer, structured_data, structured_config)

        legacy_html: Optional[str] = None
        if args.legacy_dir.exists():
            legacy_path = _find_section(args.legacy_dir, slug)
            if legacy_path is not None:
                legacy_data = _load_json(legacy_path)
                legacy_html = _render_with_transformer(args.legacy_transformer, legacy_data)

        notes = feedback.get(slug, {}).get("notes")
        preview_html = _build_preview_html(
            slug,
            structured_html,
            legacy_html,
            notes=notes,
            diff_enabled=not args.no_diff,
        )

        output_path = args.output_dir / f"{slug}.html"
        output_path.write_text(preview_html, encoding="utf-8")
        written.append(output_path)

    if written:
        print("Generated previews:")
        for path in written:
            print(f" - {path}")
    else:
        print("No previews generated. Check slug/glob filters.")


if __name__ == "__main__":
    main()



