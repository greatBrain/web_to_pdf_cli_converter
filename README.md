## A very simple, rustic, basic and probably unnecessary web converter to pdf file.

### Instalación

```bash
sudo apt install libpango-1.0-0 libpangoft2-1.0-0   # dependencias de sistema de WeasyPrint
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt                     # dependencias fijadas + el propio proyecto (-e .)
```

### Uso

```bash
web-to-pdf https://ejemplo.com/blog/mi-post                       # -> mi-post.pdf
web-to-pdf https://ejemplo.com/blog/mi-post -o pdfs/              # -> pdfs/mi-post.pdf
web-to-pdf https://ejemplo.com/blog/mi-post -o lecturas/post.pdf
python -m web_to_pdf https://ejemplo.com/blog/mi-post             # equivalente
```

El código de `src/` se instala como el paquete `web_to_pdf`, así que no se ejecuta con `python src/cli.py`.
