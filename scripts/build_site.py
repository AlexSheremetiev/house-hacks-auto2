#!/usr/bin/env python3
"""Генерирует сайт (HTML) + RSS-ленту для Яндекс Дзена."""

import pathlib
import re
import textwrap
from datetime import datetime, timezone
import email.utils as eut

import markdown
from feedgen.feed import FeedGenerator
from lxml import etree as LET

# ───────────────────────────────────────────
# 0. настройки
root = pathlib.Path("site")              # куда кладём файлы
site_url = "http://proste-hack.ru"       # без закрывающего «/»
channel_title = "Проще, чем кажется"
channel_descr = "Автолайфхаки и бытовые трюки"

# зарегистрируем пространство имён для кастомных тегов Дзена
LET.register_namespace("yandex", "http://news.yandex.ru")

# ───────────────────────────────────────────
# 1. каждый Markdown (*.md) → HTML (*.html)
for md_path in root.glob("*.md"):
    html_body = markdown.markdown(md_path.read_text(encoding="utf-8"))
    html_page = f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><title>{md_path.stem}</title></head>
<body>{html_body}</body></html>"""
    (root / f"{md_path.stem}.html").write_text(html_page, encoding="utf-8")

# ───────────────────────────────────────────
# 2. index.html с перечнем статей
links = [f'<li><a href="{p.stem}.html">{p.stem}</a></li>' for p in root.glob("*.md")]
index_html = f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><title>Proste-hack</title></head>
<body><h1>Статьи</h1><ul>{''.join(links)}</ul></body></html>"""
(root / "index.html").write_text(index_html, encoding="utf-8")

# ───────────────────────────────────────────
# 3. RSS-лента, соответствующая требованиям Дзена
fg = FeedGenerator()
fg.title(channel_title)
fg.link(href=f"{site_url}/", rel="alternate")
fg.description(channel_descr)
fg.language("ru")

# перебираем md-файлы (новые статьи первыми)
for md_path in sorted(root.glob("*.md"), reverse=True):
    raw_md = md_path.read_text(encoding="utf-8")

    # HTML-версия полного текста для <yandex:full-text>
    full_html = markdown.markdown(raw_md)

    # «чистый» анонс ≤ 500 симв. без Markdown
    plain = re.sub(r'#.*?\n', '', raw_md)          # убираем заголовки ## ...
    plain = re.sub(r'[*_`>~-]', '', plain)         # убираем markdown-символы
    plain = re.sub(r'\n+', ' ', plain).strip()
    teaser = textwrap.shorten(plain, width=500, placeholder="…")

    # формируем <item>
    fe = fg.add_entry()
    fe.title(md_path.stem)
    fe.link(href=f"{site_url}/{md_path.stem}.html")
    fe.description(teaser)
    fe.guid(f"{site_url}/{md_path.stem}.html", permalink=True)
    fe.pubDate(eut.format_datetime(datetime.now(timezone.utc)))

    # добавляем <yandex:genre> и <yandex:full-text>
    item = fe.rss_entry()  # lxml-элемент <item>
    LET.SubElement(item, "{http://news.yandex.ru}genre").text = "article"
    LET.SubElement(item, "{http://news.yandex.ru}full-text").text = full_html

# ───────────────────────────────────────────
# 4. сохраняем как site/feed.xml
fg.rss_file(root / "feed.xml")
print("✓ Сайт и RSS-лента собраны")
