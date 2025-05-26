import os, pathlib, datetime, openai, markdown, time
from suggest_provider import get_daily

openai.api_key = os.environ["OPENAI_API_KEY"]
out_dir = pathlib.Path("site")
out_dir.mkdir(exist_ok=True)

def ask_gpt(topic: str) -> str:
    """Запрашиваем GPT-4o; при 100 K TPM ждём и пробуем снова."""
    while True:
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"Напиши статью 2300–2700 знаков + FAQ по теме: {topic}. Заголовок ≤70 симв."
                }]
            )
            return resp.choices[0].message.content.strip()
        except openai.error.RateLimitError:
            print("⬇  TPM limit, waiting 70 s…")
            time.sleep(70)

for topic in get_daily():                 # 30 подсказок
    md = ask_gpt(topic)

    slug  = "-".join(topic.split()[:6])
    fname = f"{datetime.date.today()}-{slug}.md"
    (out_dir / fname).write_text(md, encoding="utf-8")

    time.sleep(30)                        # пауза для RPM-лимита
