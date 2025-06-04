import pathlib
from datetime import datetime, timezone
import email.utils as eut          # для красивого pubDate в RFC 1123
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
fg.title('Проще, чем кажется')
fg.link(href='http://proste-hack.ru/', rel='alternate')
fg.description('Автолайфхаки и бытовые трюки')
fg.language('ru')

# объявляем namespace, требуемый Яндекс.Дзеном
fg._nsmap['yandex'] = 'http://news.yandex.ru'

for md_path in sorted(root.glob('*.md'), reverse=True):
    full = md_path.read_text(encoding='utf-8')

    fe = fg.add_entry()                                   # 1) создаём элемент
    fe.title(md_path.stem)
    fe.link(href=f'http://proste-hack.ru/{md_path.stem}.html')
    fe.description(full[:500])                            # анонс ≤ 500 симв.
    fe.guid(f'http://proste-hack.ru/{md_path.stem}.html', permalink=True)

    # полный текст — кастомный тег <yandex:full-text>
    fe._element('yandex:full-text').text = full           # 2) добавляем тег

    # дата публикации в GMT, как просит Дзен
    fe.pubDate(eut.format_datetime(datetime.now(timezone.utc)))

# ---------- 4. сохраняем RSS-фид ----------
fg.rss_file(root / 'feed.xml')
