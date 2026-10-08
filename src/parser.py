import re

from bs4 import BeautifulSoup, Comment, Tag

from . import WebToPdfError

STRIP_TAGS = (
    "script", "style", "noscript", "template", "iframe", "svg", "canvas",
    "form", "button", "input", "select", "textarea", "dialog",
    "nav", "footer", "aside",
)
WRAPPER_TAGS = ("div", "section", "article", "main", "header")
BLOCK_TAGS = (
    *WRAPPER_TAGS, "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "dl", "pre", "blockquote", "table", "figure", "hr",
)
KEEP_TAGS = {
    "h1", "h2", "h3", "h4", "h5", "h6", "p", "br", "hr",
    "ul", "ol", "li", "dl", "dt", "dd",
    "pre", "code", "kbd", "samp", "blockquote",
    "a", "em", "strong", "i", "b", "sup", "sub", "mark",
    "img", "figure", "figcaption",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption",
}
KEEP_ATTRS = {
    "a": {"href"},
    "img": {"src", "alt"},
    "ol": {"start"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan"},
}
DROP_IF_EMPTY = ("p", "li", "ul", "ol", "blockquote", "figure", "a", "h1", "h2", "h3", "h4", "h5", "h6")
PERMALINK_MARKS = {"¶", "#", "§", "🔗"}
NOISE = re.compile(
    r"^(comments?|share|sharing|social|related|newsletter|subscribe|promo|ads?|advert\w*"
    r"|cookie\w*|sidebar|breadcrumbs?|author-bio)([-_].*)?$",
    re.IGNORECASE,
)


def extract_article(html: str) -> tuple[str, str]:
    """Return (title, body_html) with only the readable content."""
    soup = BeautifulSoup(html, "html.parser")

    for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
        comment.extract()
    _decompose_all(soup.find_all(STRIP_TAGS))
    _decompose_all(a for a in soup.find_all("a") if a.get_text(strip=True) in PERMALINK_MARKS)

    container = _main_container(soup)
    title = _title(soup, container)

    if container.name == "body":
        _decompose_all(container.find_all("header"))
    _decompose_all(tag for tag in container.find_all(True) if _is_noise(tag))

    for tag in container.find_all(True):
        if not tag.decomposed:
            _sanitize(tag)
    for tag in reversed(container.find_all(DROP_IF_EMPTY)):
        if not tag.get_text(strip=True) and tag.find("img") is None:
            tag.decompose()

    if not container.get_text(strip=True):
        raise WebToPdfError("No readable content found (is the page rendered with JavaScript?)")

    if container.find("h1") is None:
        heading = soup.new_tag("h1")
        heading.string = title
        container.insert(0, heading)

    return title, container.decode_contents()


def _main_container(soup: BeautifulSoup) -> Tag:
    if articles := soup.find_all("article"):
        return max(articles, key=lambda tag: len(tag.get_text(strip=True)))
    return soup.find("main") or soup.find(attrs={"role": "main"}) or soup.body or soup


def _title(soup: BeautifulSoup, container: Tag) -> str:
    if (h1 := container.find("h1")) and (text := h1.get_text(" ", strip=True)):
        return text
    if (og := soup.find("meta", property="og:title")) and og.get("content", "").strip():
        return og["content"].strip()
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return "Untitled"


def _is_noise(tag: Tag) -> bool:
    if tag.decomposed:
        return False
    if tag.get("aria-hidden") == "true" or tag.has_attr("hidden"):
        return True
    return any(NOISE.match(token) for token in [*tag.get("class", []), tag.get("id", "")] if token)


def _sanitize(tag: Tag) -> None:
    if tag.name in WRAPPER_TAGS:
        # A "leaf" div with text is a de facto paragraph; if it wraps blocks, it is redundant.
        if tag.find(BLOCK_TAGS) is None and tag.get_text(strip=True):
            tag.name = "p"
        else:
            tag.unwrap()
            return

    if tag.name == "img":
        src = tag.get("data-src") or tag.get("data-original") or tag.get("src")
        if not src or src.startswith("data:"):
            tag.decompose()
            return
        tag["src"] = src

    if tag.name not in KEEP_TAGS:
        tag.unwrap()
        return

    allowed = KEEP_ATTRS.get(tag.name, set())
    tag.attrs = {name: value for name, value in tag.attrs.items() if name in allowed}


def _decompose_all(tags) -> None:
    for tag in list(tags):
        if not tag.decomposed:
            tag.decompose()
