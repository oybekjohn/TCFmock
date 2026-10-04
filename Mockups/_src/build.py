#!/usr/bin/env python3
"""
Mockup yig'uvchi (build).

Manba:   Mockups/_src/pages/*.html     — sahifa tanasi (front-matter bilan)
         Mockups/_src/partials/*.html  — takrorlanuvchi bo'laklar (<!--#include nom-->)
         Mockups/_src/i18n/{uz,ru,fr,en}.json — matnlar 4 tilda
         Mockups/_src/assets/          — CSS, JS, shrift, rasm
Natija:  Mockups/*.html — har biri to'liq mustaqil (shrift, CSS, JS ichida),
         internet yoki serversiz ikki marta bosib ochiladi.

Ishga tushirish:  python3 Mockups/_src/build.py
"""
import base64, html, json, pathlib, re, sys

SRC = pathlib.Path(__file__).resolve().parent
OUT = SRC.parent
LANGS = ['uz', 'ru', 'fr', 'en']

I18N = {l: json.loads((SRC / 'i18n' / f'{l}.json').read_text(encoding='utf-8')) for l in LANGS}


def check_i18n():
    base = set(I18N['uz'])
    ok = True
    for l in LANGS[1:]:
        miss, extra = base - set(I18N[l]), set(I18N[l]) - base
        if miss: print(f'  ! {l}.json da yo\'q kalitlar: {sorted(miss)}'); ok = False
        if extra: print(f'  ! {l}.json da ortiqcha kalitlar: {sorted(extra)}'); ok = False
    return ok


def asset(name):
    return (SRC / 'assets' / name).read_text(encoding='utf-8')


def data_uri(name):
    mime = {'jpg': 'image/jpeg', 'png': 'image/png', 'svg': 'image/svg+xml', 'woff2': 'font/woff2'}[name.rsplit('.', 1)[1]]
    return f'data:{mime};base64,' + base64.b64encode((SRC / 'assets' / name).read_bytes()).decode()


def font_css():
    out = []
    for line in asset('fonts.ranges').splitlines():
        fname, rng = line.split('|')
        out.append("@font-face{font-family:'Manrope';font-style:normal;font-weight:200 800;font-display:swap;"
                   f"src:url({data_uri(fname)}) format('woff2');unicode-range:{rng};}}")
    return '\n'.join(out)


def minify_css(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r'\s*\n\s*', '\n', css)
    css = re.sub(r'\n+', '\n', css)
    return css.strip()


def parse_page(text):
    m = re.match(r'\s*<!--(.*?)-->\s*\n', text, re.S)
    meta = {}
    if m:
        for line in m.group(1).strip().splitlines():
            if ':' in line:
                k, v = line.split(':', 1); meta[k.strip()] = v.strip()
        text = text[m.end():]
    return meta, text


def include(text, depth=0):
    def rep(m):
        part = (SRC / 'partials' / f'{m.group(1)}.html').read_text(encoding='utf-8')
        return include(part, depth + 1)
    return re.sub(r'<!--#include ([\w-]+)-->', rep, text)


UZ = I18N['uz']


def fill_defaults(body, page):
    """Bo'sh data-i18n elementlarga o'zbekcha matnni qo'yadi (JS o'chiq bo'lsa ham ko'rinsin)."""
    def need(key):
        if key not in UZ:
            sys.exit(f'XATO: {page}: "{key}" kaliti uz.json da yo\'q')
        return UZ[key]
    # <tag ... data-i18n="k" ...></tag>
    body = re.sub(r'(<(\w+)\b[^>]*\sdata-i18n="([^"]+)"(?![^>]*data-i18n-attr)[^>]*>)(</\2>)',
                  lambda m: m.group(1) + html.escape(need(m.group(3)), quote=False) + m.group(4), body)
    # <tag ... data-i18n-html="k" ...></tag>
    body = re.sub(r'(<(\w+)\b[^>]*\sdata-i18n-html="([^"]+)"[^>]*>)(</\2>)',
                  lambda m: m.group(1) + need(m.group(3)) + m.group(4), body)
    # data-i18n-attr="placeholder" -> placeholder="..."
    def attr(m):
        tag = m.group(0)
        key = re.search(r'data-i18n="([^"]+)"', tag).group(1)
        a = re.search(r'data-i18n-attr="([^"]+)"', tag).group(1)
        val = html.escape(need(key), quote=True)
        if re.search(rf'\s{a}="[^"]*"', tag):
            return re.sub(rf'(\s{a}=")[^"]*(")', lambda x: x.group(1) + val + x.group(2), tag)
        return tag[:-1] + f' {a}="{val}">'
    body = re.sub(r'<\w+\b[^>]*data-i18n-attr="[^"]+"[^>]*>', attr, body)
    # {{t:key}} -> faqat matn (o'zbekcha)
    body = re.sub(r'\{\{t:([\w.\-]+)\}\}', lambda m: html.escape(need(m.group(1)), quote=False), body)
    # {{asset:fayl}} -> data URI
    body = re.sub(r'\{\{asset:([\w.\-]+)\}\}', lambda m: data_uri(m.group(1)), body)
    return body


MOCK_DOCK = '''
<div class="mk-dock{raised}">
<a href="index.html" class="mk-back" title="Barcha oynalar">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M11 18l-6-6 6-6"/></svg>
  <span>Barcha oynalar</span>
</a>
<span class="mk-tag">MOCKUP · {label}</span>
</div>'''

MOCK_CSS = '''
.mk-dock{position:fixed;left:18px;bottom:18px;z-index:999;display:flex;align-items:center;gap:8px;pointer-events:none}
.mk-dock>*{pointer-events:auto}
.mk-dock--raised{bottom:92px}
.mk-dock--right{left:auto;right:18px}.mk-dock--right .mk-tag{left:auto;right:0}
.mk-back{display:inline-flex;align-items:center;gap:8px;background:#28004d;color:#fff;padding:10px 16px;border-radius:999px;font-weight:800;font-size:13.5px;box-shadow:0 10px 28px rgba(40,0,77,.35);transition:transform .18s}
.mk-back:hover{transform:translateY(-2px)}
.mk-tag{position:absolute;left:0;bottom:calc(100% + 8px);background:#ffec68;color:#6b5a00;white-space:nowrap;padding:6px 14px;border-radius:999px;font-weight:800;font-size:12px;letter-spacing:.06em;box-shadow:0 6px 18px rgba(0,0,0,.12);opacity:0;transform:translateY(4px);transition:opacity .15s,transform .15s;pointer-events:none}
.mk-dock:hover .mk-tag,.mk-dock:focus-within .mk-tag{opacity:1;transform:none}
@media(max-width:640px){.mk-tag,.mk-back span{display:none}.mk-back{padding:11px}.mk-dock{left:10px;bottom:10px}.mk-dock--right{left:auto;right:10px}.mk-dock--raised{bottom:80px}}'''


def build_page(path, fonts, css_cache):
    meta, body = parse_page(path.read_text(encoding='utf-8'))
    body = include(body)
    body = fill_defaults(body, path.name)
    use_i18n = meta.get('i18n', 'yes') != 'no'
    css = css_cache['base']
    for extra in filter(None, meta.get('css', '').split(',')):
        css += '\n' + css_cache[extra.strip()]
    if path.name != 'index.html':
        css += MOCK_CSS
        dock_cls = (' mk-dock--raised' if meta.get('raised') == 'yes' else '') + (' mk-dock--right' if 'admin' in path.name else '')
        body += MOCK_DOCK.replace('{raised}', dock_cls) \
                         .replace('{label}', html.escape(meta.get('mock', path.stem)))
    title_key = meta.get('title_key')
    title = UZ[title_key] if title_key else meta.get('title', 'TCF Canada Pro')
    title_tag = f'<title data-i18n="{title_key}">{html.escape(title)}</title>' if title_key else f'<title>{html.escape(title)}</title>'
    scripts = ''
    if use_i18n:
        keys = sorted(set(re.findall(r'data-i18n(?:-html)?="([^"]+)"', body)) | ({title_key} if title_key else set()))
        sub = {l: {k: I18N[l][k] for k in keys} for l in LANGS}
        scripts += '<script>window.I18N=' + json.dumps(sub, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
    scripts += '<script>\n' + asset('app.js') + '</script>'
    body_attr = meta.get('body', '')
    out = (f'<!DOCTYPE html>\n<html lang="uz">\n<head>\n<meta charset="UTF-8">\n'
           f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
           f'<meta name="robots" content="noindex">\n{title_tag}\n'
           f'<style>\n{fonts}\n{minify_css(css)}\n</style>\n</head>\n<body {body_attr}>\n'
           f'{body.strip()}\n{scripts}\n</body>\n</html>\n')
    (OUT / path.name).write_text(out, encoding='utf-8')
    return len(out.encode())


def main():
    if not check_i18n():
        sys.exit('i18n fayllarida kalitlar mos emas — tuzating.')
    fonts = font_css()
    css_cache = {p.stem: minify_css(p.read_text(encoding='utf-8')) for p in (SRC / 'assets').glob('*.css')}
    pages = sorted((SRC / 'pages').glob('*.html'))
    for p in pages:
        size = build_page(p, fonts, css_cache)
        print(f'  {p.name:32s} {size/1024:7.1f} KB')
    print(f'{len(pages)} ta sahifa yig\'ildi.')


if __name__ == '__main__':
    main()
