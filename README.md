# web-to-pdf

A small command-line tool that turns a web article or blog post into a clean, readable PDF.

It downloads the page, keeps only the article content (no menus, sidebars, cookie banners or share buttons), applies a simple print-friendly stylesheet, and renders it to an A4 PDF with page numbers and a link back to the source.

## Requirements

- Python 3.10+
- The system libraries WeasyPrint needs (Pango). On Debian/Ubuntu:

```bash
sudo apt install libpango-1.0-0 libpangoft2-1.0-0
```

## Installation

```bash
git clone https://github.com/greatBrain/web_to_pdf_cli_converter.git
cd web_to_pdf_cli_converter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` installs the pinned dependencies and the project itself, which gives you the `web-to-pdf` command.

## Usage

```bash
web-to-pdf https://example.com/blog/my-post                  # -> my-post.pdf
web-to-pdf https://example.com/blog/my-post -o pdfs/         # -> pdfs/my-post.pdf
web-to-pdf https://example.com/blog/my-post -o reading/post.pdf
```

If you leave out `https://`, it's added for you. The output file name comes from the last part of the URL.

You can also run it as a module:

```bash
python -m web_to_pdf https://example.com/blog/my-post
```

## How it works

```
URL ──> http.py ──> parser.py ──> pdf.py ──> file.pdf
       (download)   (cleanup)    (style + render)
```

- `http.py` fetches the page and handles redirects, timeouts and encodings.
- `parser.py` finds the main content (`<article>`, `<main>` or the body), strips the noise and keeps only basic tags: headings, paragraphs, lists, code, tables, images and links.
- `pdf.py` wraps the result in a reading stylesheet and renders it with WeasyPrint.
- `cli.py` ties it all together.

The code in `src/` is installed as the `web_to_pdf` package, so it can't be run directly with `python src/cli.py`.

## Limitations

- Pages that build their content with JavaScript won't work: the tool only sees the HTML the server sends.
- Content extraction is heuristic. Most blogs and articles come out fine, but some layouts may keep a bit of noise or lose part of the content.
