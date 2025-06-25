#!/usr/bin/env python3
"""
Генерирует одну Markdown-статью через OpenAI Chat Completion
и кладёт её в папку site/ как YYYY-MM-DD-<slug>.md.

• OPENAI_API_KEY берётся из переменных среды (Secrets)
• модель — gpt-3.5-turbo (можете заменить на другую доступную)
• встроен back-off на таймауты / 500 / rate-limit
"""

import os
import re
import sys
import datetime as dt
import pathlib

import backoff
import openai

# ────────────────────────────── 0. Константы
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

# ────────────────────────────── 1. Запрос к GPT
@backoff.on_exception(backoff.expo, RETRYABLE, max_time=180)
def ask_gpt(topic: str) -> str:
    """Возвращает Markdown-текст статьи по заданной теме."""
    response = openai.ChatCompletion.create(
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
    return response.choices[0].message.content.strip()

# ────────────────────────────── 2. Главный скрипт
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Использование:  python scripts/generate.py \"Тема статьи\"")

    topic = sys.argv[1]
    md_text = ask_gpt(topic)

    # Формируем slug (латиница, цифры, дефисы)
    slug = re.sub(r"[^\w\-]+", "-", topic.lower()).strip("-")
    filename = dt.date.today().strftime(f"%Y-%m-%d-{slug}.md")

    ROOT_DIR.mkdir(exist_ok=True)
    (ROOT_DIR / filename).write_text(md_text, encoding="utf-8")

    print(f"✓ Сгенерировано: site/{filename}")
