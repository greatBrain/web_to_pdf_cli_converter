import requests
from bs4.dammit import EncodingDetector

from . import WebToPdfError

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0 Safari/537.36"
)
TIMEOUT = (5, 30)  # (connect, read)


def normalize_url(url: str) -> str:
    url = url.strip()
    return url if "://" in url else f"https://{url}"


def fetch_html(url: str) -> tuple[str, str]:
    """Devuelve (html, url_final) tras seguir redirecciones."""
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        raise WebToPdfError(f"Tiempo de espera agotado al descargar {url}") from exc
    except requests.HTTPError as exc:
        raise WebToPdfError(f"El servidor respondió {exc.response.status_code} para {url}") from exc
    except requests.RequestException as exc:
        raise WebToPdfError(f"No se pudo descargar {url}: {exc}") from exc

    content_type = response.headers.get("Content-Type", "").lower()
    if content_type and "html" not in content_type:
        raise WebToPdfError(f"La URL no devuelve HTML (Content-Type: {content_type})")
    
    if "charset=" not in content_type:
        response.encoding = (
            EncodingDetector.find_declared_encoding(response.content, is_html=True) or "utf-8"
        )
    return response.text, response.url
