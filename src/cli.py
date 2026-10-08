import argparse
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

if not __package__:
    sys.exit("Este módulo no se ejecuta como script. Instala el proyecto (pip install -e .) "
             "y usa `web-to-pdf <url>` o `python -m web_to_pdf <url>`.")

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
    raw = segments[-1] if segments else parsed.hostname or "documento"
    raw = re.sub(r"\.(html?|php|aspx?|jsp)$", "", raw, flags=re.IGNORECASE)
    ascii_text = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug[:max_length].rstrip("-") or "documento"


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
        description="Convierte un artículo o post web en un PDF legible.",
    )
    parser.add_argument("url", help="URL del artículo")
    parser.add_argument(
        "-o", "--output",
        help="archivo PDF o directorio de salida (por defecto: <slug-de-la-url>.pdf)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    url = normalize_url(args.url)
    output = resolve_output(url, args.output)

    try:
        with console.status("Descargando página…") as status:
            html, final_url = fetch_html(url)
            status.update("Extrayendo contenido…")
            title, body = extract_article(html)
            status.update("Generando PDF…")
            write_pdf(title, body, final_url, output)
    except KeyboardInterrupt:
        err_console.print("[yellow]Cancelado.[/]")
        return 130
    except WebToPdfError as exc:
        err_console.print(f"[bold red]✖[/] {escape(str(exc))}")
        return 1

    console.print(f"[green]✔[/] {escape(title)}")
    console.print(f"  Guardado en [bold]{escape(str(output))}[/]")
    return 0
