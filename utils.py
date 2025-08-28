import requests
from bs4 import BeautifulSoup
from weasyprint import HTML

DEFAULT_HTML_PAGE = """
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>Documento por defecto</title>
        </head>
        <body>
            <h1>No se pudo descargar el HTML.</h1>
        </body>
    </html>
"""
def fetch_html(url: str) -> str:
    """Descarga el HTML desde la URL dada.
    Args:
        url: URL de la página a scrapear.
    Returns:
        El contenido HTML como string.
    Raises:
        RuntimeError: Si ocurre un error de conexión o HTTP.
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        raise RuntimeError(f"Error al descargar la URL: {exc}") from exc

def parse_content(html: str = DEFAULT_HTML_PAGE) -> str:
    """Parsea un objeto HTML y devuelve su contenido simplificado.
    Args:
        html: Cadena HTML de entrada.
    Returns:
        Un HTML minimal con título y párrafos extraídos.
    """
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("h1")
    title_content = title.get_text(strip=True) if title else "Sin título"
    paragraphs = [ p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True) ]

    return f"""
    <html>
        <head>
        <meta charset="utf-8">
        <title>{title_content}</title>
        </head>
        <body>
            <h1>{title_content}</h1>
            {''.join(f'<p>{p}</p>' for p in paragraphs)}
        </body>
    </html>
    """
def convert_to_pdf(html_str: str, output_file: str) -> None:
    """Convierte un HTML a PDF y lo guarda en disco.
    Args:
        html_str: Cadena HTML a renderizar.
        output_file: Nombre del archivo de salida.
    Raises:
        RuntimeError: Si ocurre un error al generar el PDF.
    """
    try:
        HTML(string=html_str).write_pdf(output_file)
    except Exception as exc:
        raise RuntimeError(f"Error al generar el PDF: {exc}") from exc