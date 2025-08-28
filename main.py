import argparse
from rich.console import Console
from rich.progress import Progress
import utils
import warnings

# Silenciar las warning internas
warnings.simplefilter("ignore", UserWarning)

def _create_arguments() -> argparse.Namespace:
    """Define y parsea los argumentos de la CLI."""
    parser = argparse.ArgumentParser(
        description="Scrapea un post y lo convierte a PDF."
    )
    parser.add_argument(
        "url",
        type=str,
        help="URL del post a convertir en PDF."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="converted_from_web.pdf",
        help="Archivo de salida (por defecto: converted_from_web.pdf)."
    )
    return parser.parse_args()

"""Ejecuta el flujo principal de la aplicación."""
def run() -> None:
    args = _create_arguments()
    console = Console()
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Procesando...", total=3)
            
            html_page = utils.fetch_html(args.url)
            progress.update(task, advance=1, description="[bright_magenta]Descargando HTML...")
            
            content = utils.parse_content(html_page)
            progress.update(task, advance=1, description="[yellow]Procesando HTML...")
            
            utils.convert_to_pdf(content, args.output)
            progress.update(task, advance=1, description="[green]Generando PDF...")
        console.print(f"\n[✔] Listo: archivo guardado en [bold green]{args.output}[/bold green]")

    except Exception as exc:
        console.print(f"[✖] Error: {exc}", style="bold red")

if __name__ == "__main__":
    run()
