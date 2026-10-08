import logging
from html import escape
from pathlib import Path

from weasyprint import HTML

from . import WebToPdfError

# WeasyPrint warns about every image or CSS property it cannot resolve; it clutters the spinner.
logging.getLogger("weasyprint").setLevel(logging.ERROR)
logging.getLogger("fontTools").setLevel(logging.ERROR)

STYLESHEET = """
@page {
    size: A4;
    margin: 22mm 20mm 24mm;
    @bottom-center {
        content: counter(page) " / " counter(pages);
        font: 8.5pt "DejaVu Sans", sans-serif;
        color: #888;
    }
}
html {
    font-family: Charter, "Bitstream Charter", Georgia, "DejaVu Serif", serif;
    font-size: 11pt;
    line-height: 1.55;
    color: #1d1d1d;
}
h1, h2, h3, h4, h5, h6 {
    font-family: "Helvetica Neue", Arial, "DejaVu Sans", sans-serif;
    line-height: 1.25;
    margin: 1.6em 0 0.5em;
    break-after: avoid;
}
h1 { font-size: 21pt; margin-top: 0; }
h2 { font-size: 15pt; }
h3 { font-size: 12.5pt; }
h4, h5, h6 { font-size: 11pt; }
p { margin: 0 0 0.85em; orphans: 3; widows: 3; }
ul, ol { margin: 0 0 0.85em; padding-left: 1.4em; }
li { margin-bottom: 0.25em; }
a { color: inherit; text-decoration: underline; text-decoration-color: #aaa; }
blockquote {
    margin: 1em 0;
    padding: 0.1em 0 0.1em 1em;
    border-left: 3px solid #ccc;
    color: #555;
}
code, kbd, samp, pre {
    font-family: "DejaVu Sans Mono", Menlo, Consolas, monospace;
    font-size: 0.85em;
}
code { background: #f3f3f3; padding: 0.05em 0.25em; border-radius: 3px; }
pre {
    background: #f6f6f6;
    border: 1px solid #e4e4e4;
    border-radius: 4px;
    padding: 0.7em 0.9em;
    line-height: 1.4;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    break-inside: avoid;
}
pre code { background: none; padding: 0; font-size: inherit; }
img { max-width: 100%; height: auto; }
figure { margin: 1em 0; break-inside: avoid; }
figcaption { font-size: 9pt; color: #666; margin-top: 0.3em; }
table { border-collapse: collapse; margin: 1em 0; font-size: 9.5pt; }
th, td { border: 1px solid #ddd; padding: 0.3em 0.5em; text-align: left; }
hr { border: none; border-top: 1px solid #ddd; margin: 1.5em 0; }
.source { margin-top: 2.5em; font-size: 8.5pt; color: #888; overflow-wrap: anywhere; }
"""


def build_document(title: str, body: str, source_url: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{escape(title)}</title>
<style>{STYLESHEET}</style>
</head>
<body>
{body}
<p class="source">Source: <a href="{escape(source_url)}">{escape(source_url)}</a></p>
</body>
</html>"""


def write_pdf(title: str, body: str, source_url: str, output: Path) -> None:
    document = build_document(title, body, source_url)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        HTML(string=document, base_url=source_url).write_pdf(output)
    except OSError as exc:
        raise WebToPdfError(f"Could not write {output}: {exc}") from exc
