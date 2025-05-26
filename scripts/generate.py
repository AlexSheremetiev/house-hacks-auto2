import os, pathlib, datetime, openai, markdown, time
from suggest_provider import get_daily

openai.api_key = os.environ["OPENAI_API_KEY"]     #  ← вернуть
out_dir = pathlib.Path("site")                    #  ← вернуть
out_dir.mkdir(exist_ok=True)                      #  ← вернуть

for topic in get_daily():         # 30 подсказок
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user",
                   "content": f"Напиши статью 2300–2700 знаков + FAQ по теме: {topic}. Заголовок ≤70 симв."}]
    )
    md = resp.choices[0].message.content.strip()
    slug  = "-".join(topic.split()[:6])
    fname = f"{datetime.date.today()}-{slug}.md"
    (out_dir / fname).write_text(md, encoding="utf-8")

    time.sleep(21)   # ≤ 3 запросов в минуту
