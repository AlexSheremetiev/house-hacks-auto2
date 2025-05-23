Add file ▸ Create new file
File name: scripts/generate.py
import os, pathlib, datetime, openai, markdown
from suggest_provider import get_daily

openai.api_key = os.environ["OPENAI_API_KEY"]
out_dir = pathlib.Path("site")
out_dir.mkdir(exist_ok=True)

for topic in get_daily():
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user",
                   "content": f"Напиши статью 2300–2700 знаков + FAQ по теме: {topic}. Заголовок ≤70 симв."}]
    )
    md = resp.choices[0].message.content.strip()
    slug = "-".join(topic.split()[:6])
    fname = f"{datetime.date.today()}-{slug}.md"
    (out_dir / fname).write_text(md, encoding="utf-8")
