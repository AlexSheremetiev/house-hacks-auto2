#!/usr/bin/env python3
"""
Генерирует одну Markdown-статью через OpenAI Chat Completion
и кладёт её в site/ как YYYY-MM-DD-<slug>.md.
Если квота OpenAI исчерпана — создаёт stub-статью и завершает работу без ошибки.
"""

import os, re, sys, datetime as dt, pathlib, backoff, openai
from openai.error import OpenAIError, RateLimitError

MODEL      = "gpt-3.5-turbo"
MAX_TOKENS = 800
ROOT_DIR   = pathlib.Path("site")
openai.api_key = os.environ["OPENAI_API_KEY"]

RETRYABLE = (
    openai.error.Timeout,
    openai.error.APIError,
    openai.error.APIConnectionError,
    openai.error.RateLimitError,
)

@backoff.on_exception(backoff.expo, RETRYABLE, max_time=180)
def ask_gpt(topic: str) -> str:
    """Пытается получить Markdown-статью; бросает OpenAIError, если не вышло."""
    resp = openai.ChatCompletion.create(
        model       = MODEL,
        temperature = 0.7,
        max_tokens  = MAX_TOKENS,
        stream      = False,
        messages = [
            {"role": "system",
             "content": "Ты русский блогер-лайфхакер. Пиши понятно, с подзаголовками и шагами."},
            {"role": "user",
             "content": f"Напиши статью-инструкцию: {topic}"},
        ],
    )
    return resp.choices[0].message.content.strip()

def slugify(text: str) -> str:
    return re.sub(r"[^\w\-]+", "-", text.lower()).strip("-")

def save_article(fname: str, md_text: str) -> None:
    ROOT_DIR.mkdir(exist_ok=True)
    (ROOT_DIR / fname).write_text(md_text, encoding="utf-8")
    print(f"✓ Сохранено: site/{fname}")

# ──────────────────────────────────────────  main
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Использование: python scripts/generate.py \"Тема статьи\"")

    topic = sys.argv[1]
    today = dt.date.today().strftime("%Y-%m-%d")
    fname = f"{today}-{slugify(topic)}.md"

    try:
        md = ask_gpt(topic)
    except (OpenAIError, RateLimitError) as e:
        # Квота исчерпана или другая ошибка — пишем stub-файл
        print(f"⚠ OpenAI error: {e}. Создаю заглушечную статью.")
        md = f"# Пауза на генерацию\n\n" \
             f"Сервис OpenAI временно недоступен (лимит или ошибка). " \
             f"Попробуем снова в следующем запуске.\n"
        fname = f"{today}-stub.md"

    save_article(fname, md)
