import pathlib
from datetime import datetime, timezone
import email.utils as eut           # для pubDate в RFC 1123
import markdown
from feedgen.feed import FeedGenerator

root = pathlib.Path("site")

# ---------- 1. *.md → *.html ----------
for md in root.glob("*.md"):
    html = markdown.markdown(md.read_text(encoding="utf-8"))
    (root / f"{md.stem}.html").write_text(f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><title>{md.stem}</title></head>
<body>{html}</body></html>""", encoding="utf-8")

# ---------- 2. index.html ----------
links = [f'<li><a href="{p.stem}.html">{p.stem}</a></li>' for p in root.glob("*.md")]
(root / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><title>Proste-hack</title></head>
<body><h1>Статьи</h1><ul>{''.join(links)}</ul></body></html>""", encoding="utf-8")

# ---------- 3. RSS ----------
fg = FeedGenerator()
fg.title('Проще, чем кажется')
fg.link(href='http://proste-hack.ru/', rel='alternate')
fg.description('Автолайфхаки и бытовые трюки')
fg.language('ru')

# — добавляем namespace Яндекса прямо в корневой тег
fg._feed.attrib['xmlns:yandex'] = 'http://news.yandex.ru'

for md in sorted(root.glob('*.md'), reverse=True):
    full = md.read_text(encoding='utf-8')
    fe = fg.add_entry()
    fe.title(md.stem)
    fe.link(href=f'http://proste-hack.ru/{md.stem}.html')
    fe.description(full[:500])                               # анонс ≤ 500 симв.
    fe.guid(f'http://proste-hack.ru/{md.stem}.html', permalink=True)

    # полный текст
    fe._element('yandex:full-text').text = full

    fe.pubDate(eut.format_datetime(datetime.now(timezone.utc)))

# ---------- 4. сохраняем ----------
fg.rss_file(root / "feed.xml")
