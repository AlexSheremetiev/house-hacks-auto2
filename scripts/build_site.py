import pathlib
import markdown
from feedgen.feed import FeedGenerator
from datetime import datetime

root = pathlib.Path("site")          # здесь лежат *.md-файлы

# 1. Конвертируем каждый *.md → *.html
for md_path in root.glob("*.md"):
    html = markdown.markdown(md_path.read_text(encoding="utf-8"))
    (root / f"{md_path.stem}.html").write_text(html, encoding="utf-8")

# 2. Собираем RSS-фид
fg = FeedGenerator()
fg.title("Proste-hack")
fg.link(href="https://www.proste-hack.ru/", rel="alternate")
fg.description("Автоблог")

for md_path in sorted(root.glob("*.md"), reverse=True):
    fe = fg.add_entry()
    fe.title(md_path.stem)
    fe.link(href=f"https://www.proste-hack.ru/{md_path.stem}.html")
    fe.description(md_path.read_text(encoding="utf-8")[:500])

fg.rss_file(root / "feed.xml")      # сохраняем RSS в site/feed.xml
