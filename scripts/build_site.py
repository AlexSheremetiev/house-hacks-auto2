import pathlib, markdown, email.utils as eut
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import xml.etree.ElementTree as ET

# зарегистрируем пространство имён для Яндекса
ET.register_namespace('yandex', 'http://news.yandex.ru')

root = pathlib.Path("site")

# ---------- 1. md → html ----------
for md_path in root.glob("*.md"):
    html = markdown.markdown(md_path.read_text(encoding="utf-8"))
    (root / f"{md_path.stem}.html").write_text(
        f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><title>{md_path.stem}</title></head>
<body>{html}</body></html>""",
        encoding="utf-8")

# ---------- 2. index.html ----------
links = [f'<li><a href="{p.stem}.html">{p.stem}</a></li>' for p in root.glob("*.md")]
(root / "index.html").write_text(
    f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><title>Proste-hack</title></head>
<body><h1>Статьи</h1><ul>{''.join(links)}</ul></body></html>""",
    encoding="utf-8")

# ---------- 3. RSS ----------
fg = FeedGenerator()
fg.title('Проще, чем кажется')
fg.link(href='http://proste-hack.ru/', rel='alternate')
fg.description('Автолайфхаки и бытовые трюки')
fg.language('ru')

for md_path in sorted(root.glob("*.md"), reverse=True):
    full = md_path.read_text(encoding="utf-8")

    fe = fg.add_entry()
    fe.title(md_path.stem)
    fe.link(href=f'http://proste-hack.ru/{md_path.stem}.html')
    fe.description(full[:500])
    fe.guid(f'http://proste-hack.ru/{md_path.stem}.html', permalink=True)
    fe.pubDate(eut.format_datetime(datetime.now(timezone.utc)))

    # <yandex:full-text>
    ET.SubElement(
        fe.rss_entry(),                          # ← элемент <item>
        '{http://news.yandex.ru}full-text'
    ).text = full

# ---------- 4. save ----------
fg.rss_file(root / "feed.xml")
