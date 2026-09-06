#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the site from content data files + template.

Usage:
  python3 tools/build.py            # render templates/index.html -> index.html (in place)
  python3 tools/build.py --check    # render to stdout/temp and verify byte-identical to index.html
  python3 tools/build.py --out FILE # write rendered output to FILE

Placeholder syntax in the template:
  {{file.key.path}}    -> text: value is HTML-escaped (safe for user input like `&`)
  {{{file.key.path}}}  -> html: value injected verbatim (must contain valid markup)
"""
import argparse
import html as html_mod
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TPL = ROOT / "templates" / "index.html"
CONTENT_DIR = ROOT / "content"
PH_TEXT = re.compile(r"\{\{([a-zA-Z0-9_.-]+)\}\}")
PH_HTML = re.compile(r"\{\{\{([a-zA-Z0-9_.-]+)\}\}\}")


def load_content():
    data = {}
    for f in sorted(CONTENT_DIR.glob("*.json")):
        data[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    return data


def lookup(data, dotted):
    node = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(f"missing content key: {dotted}")
        node = node[part]
    return node


def render(data):
    tpl = TPL.read_text(encoding="utf-8")

    # html placeholders first (verbatim), then text placeholders (escaped)
    def repl_html(m):
        return str(lookup(data, m.group(1)))

    def repl_text(m):
        return html_mod.escape(str(lookup(data, m.group(1))), quote=False)

    out, n_html = PH_HTML.subn(repl_html, tpl)
    out, n_text = PH_TEXT.subn(repl_text, out)
    return out, n_html + n_text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="render to memory and verify byte-identity with index.html")
    ap.add_argument("--out", type=str, default=None,
                    help="write rendered output to this file (default: ROOT/index.html)")
    args = ap.parse_args()

    data = load_content()
    out, n = render(data)
    print(f"rendered {n} placeholders")

    if args.check:
        current = (ROOT / "index.html").read_bytes()
        if out.encode("utf-8") == current:
            print("CHECK PASSED: rendered output is byte-identical to index.html")
        else:
            print("CHECK FAILED: rendered output differs from index.html", file=sys.stderr)
            sys.exit(1)
        return

    target = pathlib.Path(args.out) if args.out else ROOT / "index.html"
    target.write_text(out, encoding="utf-8")
    print(f"written: {target}")


if __name__ == "__main__":
    main()