#!/usr/bin/env python3
"""
emoji_utils.py

A small, standalone Python utility for working with emoji shortcodes.
Features:
- Mapping of common shortcode -> emoji.
- shortcode_to_emoji(text): replaces :shortcode: with emoji.
- emoji_to_shortcode(text): replaces emoji characters with :shortcode: where known.
- list_shortcodes(): returns available shortcodes.
- random_emoji(count=1): returns random emoji(s).
- CLI: replace, revert, list, random, serve (simple HTTP page showing list)

No external dependencies.

Author: ChatGPT
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import argparse
import json
import random
import re
import sys
from typing import Dict, List

# Minimal emoji map. Expand as needed.
EMOJI_MAP: Dict[str, str] = {
    "smile": "😄",
    "grin": "😁",
    "joy": "😂",
    "thumbsup": "👍",
    "thumbsdown": "👎",
    "heart": "❤️",
    "sparkles": "✨",
    "fire": "🔥",
    "star": "⭐",
    "100": "💯",
    "check": "✅",
    "x": "❌",
    "rocket": "🚀",
    "party": "🥳",
    "thinking": "🤔",
    "sob": "😭",
    "pray": "🙏",
    "ok_hand": "👌",
    "clap": "👏",
    "wave": "👋",
    "tada": "🎉",
}

# Reverse map for emoji -> shortcode
REVERSE_MAP: Dict[str, str] = {v: k for k, v in EMOJI_MAP.items()}

SHORTCODE_PATTERN = re.compile(r":([a-zA-Z0-9_+-]+):")


def shortcode_to_emoji(text: str) -> str:
    """Replace occurrences of :shortcode: with the corresponding emoji.

    Unknown shortcodes are left unchanged.
    """

    def repl(match: re.Match) -> str:
        key = match.group(1)
        return EMOJI_MAP.get(key, match.group(0))

    return SHORTCODE_PATTERN.sub(repl, text)


def emoji_to_shortcode(text: str) -> str:
    """Replace known emoji characters with their :shortcode: equivalents.

    Unknown emoji characters are left unchanged.
    """
    # For safety, iterate over known emojis and replace them.
    result = text
    for emo, code in REVERSE_MAP.items():
        result = result.replace(emo, f":{code}:")
    return result


def list_shortcodes() -> List[str]:
    """Return a sorted list of available shortcodes."""
    return sorted(EMOJI_MAP.keys())


def random_emoji(count: int = 1) -> List[str]:
    """Return a list of random emoji characters from the map."""
    if count < 1:
        return []
    return random.choices(list(EMOJI_MAP.values()), k=count)


def _serve(port: int = 8000) -> None:
    """Serve a simple HTML page listing shortcodes and emojis."""
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Emoji Utils</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial; padding: 2rem; }
          table { border-collapse: collapse; width: 100%; max-width: 800px; }
          th, td { padding: 0.5rem 1rem; border-bottom: 1px solid #eee; text-align: left; }
          th { background: #f7f7f7; }
          .emoji { font-size: 1.5rem; }
        </style>
      </head>
      <body>
        <h1>Emoji utils — shortcodes</h1>
        <table>
          <thead><tr><th>Shortcode</th><th>Emoji</th></tr></thead>
          <tbody>
    """
    for sc in list_shortcodes():
        html += f"<tr><td>:{sc}:</td><td class=\"emoji\">{EMOJI_MAP[sc]}</td></tr>\n"
    html += """
          </tbody>
        </table>
        <p>Use this page to copy/paste shortcodes or emoji characters.</p>
      </body>
    </html>
    """

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
            else:
                super().do_GET()

    server = HTTPServer(("", port), Handler)
    print(f"Serving emoji list at http://localhost:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
        server.server_close()


def _cli_args():
    p = argparse.ArgumentParser(description="emoji_utils — replace or list emoji shortcodes")
    sub = p.add_subparsers(dest="cmd")

    # replace command
    r = sub.add_parser("replace", help="Replace :shortcode: with emoji in a text string (prints result)")
    r.add_argument("text", nargs="+", help="Text to transform; wrap in quotes if needed")

    # revert command
    rev = sub.add_parser("revert", help="Replace known emoji with :shortcode: in a text string (prints result)")
    rev.add_argument("text", nargs="+", help="Text to transform; wrap in quotes if needed")

    # list command
    sub.add_parser("list", help="List available shortcodes")

    # random command
    rand = sub.add_parser("random", help="Print random emoji(s)")
    rand.add_argument("-n", "--count", type=int, default=1, help="Number of emoji to return")

    # serve command
    serve = sub.add_parser("serve", help="Serve a tiny webpage showing the emoji list")
    serve.add_argument("-p", "--port", type=int, default=8000, help="Port to serve on")

    return p.parse_args()


def main():
    args = _cli_args()
    if args.cmd == "replace":
        text = " ".join(args.text)
        out = shortcode_to_emoji(text)
        print(out)
    elif args.cmd == "revert":
        text = " ".join(args.text)
        out = emoji_to_shortcode(text)
        print(out)
    elif args.cmd == "list":
        for sc in list_shortcodes():
            print(f":{sc}: \t{EMOJI_MAP[sc]}")
    elif args.cmd == "random":
        items = random_emoji(args.count)
        print(" ".join(items))
    elif args.cmd == "serve":
        _serve(args.port)
    else:
        print("No command specified. Use --help for usage.")


if __name__ == "__main__":
    main()
