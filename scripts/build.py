"""Valida referências locais e gera somente os arquivos públicos em dist/."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import shutil

ROOT = Path(__file__).resolve().parent.parent
PAGES = [ROOT / 'index.html', *ROOT.glob('*/**/*.html')]
PAGES = [p for p in PAGES if 'dist' not in p.relative_to(ROOT).parts]
class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
    def handle_starttag(self, tag, attrs):
        self.refs.extend(value for name, value in attrs if name in ('href', 'src') and value)

for page in PAGES:
    parser = References()
    parser.feed(page.read_text())
    for ref in parser.refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc or not url.path:
            continue
        assert not url.path.startswith('/'), f'Link incompatível com subdiretórios: {page}: {ref}'
        target = (page.parent / unquote(url.path)).resolve()
        assert target.is_relative_to(ROOT), f'Referência fora do projeto: {ref}'
        assert target.exists(), f'Link ausente em {page.relative_to(ROOT)}: {ref}'
        if target.is_dir():
            assert (target / 'index.html').is_file(), f'Pasta sem página inicial: {target}'

# A URL antiga continua servindo exatamente a mesma simulação.
assert (ROOT/'alarme_de_incendio/index.html').read_bytes() == (ROOT/'alarme_de_incendio/laboratorio_simplex_compacto.html').read_bytes()
output = ROOT / 'dist'
if output.exists():
    shutil.rmtree(output)
output.mkdir()
for name in ('index.html', '404.html', '.nojekyll', 'assets', 'caldeira', 'clima', 'alarme_de_incendio'):
    source = ROOT / name
    if source.is_dir():
        shutil.copytree(source, output / name)
    else:
        shutil.copy2(source, output / name)
print(f'{len(PAGES)} páginas verificadas; publicação estática gerada em dist/.')
