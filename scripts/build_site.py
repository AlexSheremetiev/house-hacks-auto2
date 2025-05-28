import pathlib
from datetime import datetime, timezone          # ← добавили timezone
import markdown
from feedgen.feed import FeedGenerator

# Папка, где лежат будущие файлы сайта
root = pathlib.Path("site")

# ---------- 1. конвертируем каждый *.md → *.html ----------
for md_path in root.glob("*.md"):
    html_body = markdown.markdown(md_path.read_text(encoding="utf-8"))
    html_page = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>{md_path.stem}</title>
</head>
<body>
{html_body}
</body>
</html>"""
    (root / f"{md_path.stem}.html").write_text(html_page, encoding="utf-8")

# ---------- 2. создаём индексную страницу ----------
links = [f'<li><a href="{p.stem}.html">{p.stem}</a></li>' for p in root.glob("*.md")]
index_html = f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><title>Proste-hack</title></head>
<body>
<h1>Статьи</h1>
<ul>{''.join(links)}</ul>
</body>
</html>"""
(root / "index.html").write_text(index_html, encoding="utf-8")

# ---------- 3. собираем RSS-фид ----------
fg = FeedGenerator()
fg.title("Proste-hack")
fg.link(href="https://www.proste-hack.ru/", rel="alternate")
fg.description("Автоблог")
fg.language("ru")

for md_path in sorted(root.glob("*.md"), reverse=True):
    fe = fg.add_entry()
    fe.title(md_path.stem)
    fe.link(href=f"https://www.proste-hack.ru/{md_path.stem}.html")
    fe.description(md_path.read_text(encoding="utf-8")[:500])
    fe.pubDate(datetime.now(timezone.utc))        # ← теперь дата с тайм-зоной

# сохраняем RSS как site/feed.xml
fg.rss_file(root / "feed.xml")
