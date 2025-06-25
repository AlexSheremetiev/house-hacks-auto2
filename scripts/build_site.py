#!/usr/bin/env python3
"""Генерирует статические страницы сайта (+ RSS-ленту под требования Яндекс Дзена)."""

import pathlib
import re
import textwrap
from datetime import datetime, timezone
import email.utils as eut

import markdown
from feedgen.feed import FeedGenerator
from lxml import etree as LET

# ─────────────────────────── 0. НАСТРОЙКИ ───────────────────────────
ROOT_DIR      = pathlib.Path("site")          # куда кладём HTML и feed.xml
SITE_URL      = "http://proste-hack.ru"       # без закрывающего «/»
CHANNEL_TITLE = "Проще, чем кажется"
CHANNEL_DESCR = "Автолайфхаки и бытовые трюки"

# регистрируем неймспейс для кастомных тегов Дзена
LET.register_namespace("yandex", "http://news.yandex.ru")

# ─────────────────────────── 1. Markdown → HTML ─────────────────────
for md_path in ROOT_DIR.glob("*.md"):
    html_body = markdown.markdown(md_path.read_text(encoding="utf-8"))
    html_page = f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><title>{md_path.stem}</title></head>
<body>{html_body}</body></html>"""
    (ROOT_DIR / f"{md_path.stem}.html").write_text(html_page, encoding="utf-8")

# ─────────────────────────── 2. index.html ──────────────────────────
links = [
    f'<li><a href="{p.stem}.html">{p.stem}</a></li>'
    for p in ROOT_DIR.glob("*.md")
]
index_html = f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><title>Proste-hack</title></head>
<body><h1>Статьи</h1><ul>{''.join(links)}</ul></body></html>"""
(ROOT_DIR / "index.html").write_text(index_html, encoding="utf-8")

# ─────────────────────────── 3. RSS под Дзен ────────────────────────
fg = FeedGenerator()
fg.title(CHANNEL_TITLE)
fg.link(href=f"{SITE_URL}/", rel="alternate")
fg.description(CHANNEL_DESCR)
fg.language("ru")

# перебираем md-файлы (новые первыми)
for md_path in sorted(ROOT_DIR.glob("*.md"), reverse=True):
    raw_md = md_path.read_text(encoding="utf-8")

    full_html = markdown.markdown(raw_md)                # полный текст
    plain = re.sub(r'#.*?\n', '', raw_md)                # чистим заголовки
    plain = re.sub(r'[*_`>~-]', '', plain)               # чистим markdown-символы
    teaser = textwrap.shorten(re.sub(r'\n+', ' ', plain).strip(),
                              width=500, placeholder="…")

    # основной <item>
    fe = fg.add_entry()
    fe.title(md_path.stem)
    fe.link(href=f"{SITE_URL}/{md_path.stem}.html")
    fe.description(teaser)
    fe.guid(f"{SITE_URL}/{md_path.stem}.html", permalink=True)
    fe.pubDate(eut.format_datetime(datetime.now(timezone.utc)))

    # два обязательных тега Дзена
    item = fe.rss_entry()  # сырой lxml-элемент <item>
    LET.SubElement(item, "{http://news.yandex.ru}genre").text = "article"
    LET.SubElement(item, "{http://news.yandex.ru}full-text").text = full_html

# ─────────────────────────── 4. Сохраняем feed.xml ──────────────────
fg.rss_file(ROOT_DIR / "feed.xml")
print("✓ Сайт и RSS-лента собраны")
