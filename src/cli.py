import argparse
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

if not __package__:
    sys.exit("This module is not meant to be run as a script. Install the project (pip install -e .) "
             "and use `web-to-pdf <url>` or `python -m web_to_pdf <url>`.")

from rich.console import Console
from rich.markup import escape

from . import WebToPdfError
from .http import fetch_html, normalize_url
from .parser import extract_article
from .pdf import write_pdf

console = Console()
err_console = Console(stderr=True)


def slug_from_url(url: str, max_length: int = 80) -> str:
    parsed = urlparse(url)
    segments = [segment for segment in parsed.path.split("/") if segment]
    raw = segments[-1] if segments else parsed.hostname or "document"
    raw = re.sub(r"\.(html?|php|aspx?|jsp)$", "", raw, flags=re.IGNORECASE)
    ascii_text = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug[:max_length].rstrip("-") or "document"


def resolve_output(url: str, output: str | None) -> Path:
    filename = f"{slug_from_url(url)}.pdf"
    if output is None:
        return Path(filename)
    path = Path(output).expanduser()
    if output.endswith(("/", os.sep)) or path.is_dir():
        return path / filename
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="web-to-pdf",
        description="Convert a web article or blog post into a readable PDF.",
    )
    parser.add_argument("url", help="article URL")
    parser.add_argument(
        "-o", "--output",
        help="output PDF file or directory (default: <url-slug>.pdf)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    url = normalize_url(args.url)
    output = resolve_output(url, args.output)

    try:
        with console.status("Downloading page…") as status:
            html, final_url = fetch_html(url)
            status.update("Extracting content…")
            title, body = extract_article(html)
            status.update("Generating PDF…")
            write_pdf(title, body, final_url, output)
    except KeyboardInterrupt:
        err_console.print("[yellow]Cancelled.[/]")
        return 130
    except WebToPdfError as exc:
        err_console.print(f"[bold red]✖[/] {escape(str(exc))}")
        return 1

    console.print(f"[green]✔[/] {escape(title)}")
    console.print(f"  Saved to [bold]{escape(str(output))}[/]")
    return 0
