#!/usr/bin/env python3
"""Генерирует статические страницы + RSS-ленту под требования Яндекс Дзена."""

import pathlib, re, textwrap, email.utils as eut
from datetime import datetime, timezone

import markdown
from feedgen.feed import FeedGenerator
from lxml import etree as LET

# ─────────────── 0. НАСТРОЙКИ ───────────────
ROOT_DIR      = pathlib.Path("site")
SITE_URL      = "http://www.proste-hack.ru"      # без закрывающего «/»
CHANNEL_TITLE = "Проще, чем кажется"
CHANNEL_DESCR = "Автолайфхаки и бытовые трюки"

LET.register_namespace("yandex", "http://news.yandex.ru")

# ─────────────── 1. Markdown → HTML ─────────
for md in ROOT_DIR.glob("*.md"):
    body_html = markdown.markdown(md.read_text(encoding="utf-8"))
    (ROOT_DIR / f"{md.stem}.html").write_text(
        f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><title>{md.stem}</title></head>
<body>{body_html}</body></html>""",
        encoding="utf-8")

# ─────────────── 2. index.html ──────────────
links = [f'<li><a href="{p.stem}.html">{p.stem}</a></li>' for p in ROOT_DIR.glob("*.md")]
(ROOT_DIR / "index.html").write_text(
    f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><title>Proste-hack</title></head>
<body><h1>Статьи</h1><ul>{''.join(links)}</ul></body></html>""",
    encoding="utf-8")

# ─────────────── 3. RSS для Дзена ───────────
fg = FeedGenerator()
fg.title(CHANNEL_TITLE)
fg.link(href=f"{SITE_URL}/", rel="alternate")
fg.description(CHANNEL_DESCR)
fg.language("ru")

for md in sorted(ROOT_DIR.glob("*.md"), reverse=True):
    raw = md.read_text(encoding="utf-8")

    full_html = markdown.markdown(raw)
    plain = re.sub(r'#.*?\n', '', raw)                  # убираем заголовки
    plain = re.sub(r'[*_`>~-]', ' ', plain)             # markdown-символы → пробел
    plain = re.sub(r'\s+', ' ', plain).strip()          # схлопываем пробелы
    teaser = textwrap.shorten(plain, width=500, placeholder="…")

    fe = fg.add_entry()
    fe.title(md.stem)
    fe.link(href=f"{SITE_URL}/{md.stem}.html")
    fe.description(teaser)
    fe.guid(f"{SITE_URL}/{md.stem}.html", permalink=True)
    fe.pubDate(eut.format_datetime(datetime.now(timezone.utc)))

    item = fe.rss_entry()                               # сырой <item>
    LET.SubElement(item, "{http://news.yandex.ru}genre").text = "article"
    LET.SubElement(item, "{http://news.yandex.ru}full-text").text = plain  # ← БЕЗ HTML

# ─────────────── 4. feed.xml ────────────────
fg.rss_file(ROOT_DIR / "feed.xml")
print("✓ Сайт и RSS-лента собраны")
