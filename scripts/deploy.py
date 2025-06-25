#!/usr/bin/env python3
"""
Заливает всё из папки site/ в бакет Object Storage.
• типы контента расставляются корректно (HTML / RSS / остальное).
• если переменные окружения не заданы — скрипт завершается с кодом 0,
  чтобы workflow не падал (например, в форках без секретов).
"""

import os
import mimetypes
import pathlib
import sys

import boto3

# ─────────────────────────── 0. Читаем переменные среды
bucket  = os.getenv("BUCKET", "").strip()
region  = os.getenv("REGION", "").strip()
key_id  = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
key_sec = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()

if not all((bucket, region, key_id, key_sec)):
    print("⚠ Object Storage credentials не заданы — пропускаю deploy.", file=sys.stderr)
    sys.exit(0)        # выходим без ошибки → job останется зелёным

# ─────────────────────────── 1. Коструируем клиента S3-совместимого API
s3 = boto3.client(
    "s3",
    region_name  = region,
    endpoint_url = "https://storage.yandexcloud.net",
    aws_access_key_id     = key_id,
    aws_secret_access_key = key_sec,
)

root = pathlib.Path("site")

# ─────────────────────────── 2. Проходим по всем файлам и грузим
for file in root.rglob("*"):
    if not file.is_file():
        continue

    # правильный Content-Type
    if file.suffix == ".html":
        ctype = "text/html"
    elif file.name == "feed.xml":
        ctype = "application/rss+xml; charset=utf-8"
    else:
        ctype = mimetypes.guess_type(file.name)[0] or "application/octet-stream"

    key = str(file.relative_to(root))

    s3.upload_file(
        str(file),
        bucket,
        key,
        ExtraArgs={"ContentType": ctype, "ACL": "public-read"},
    )
    print(f"⇡  {key}  →  {bucket}")

print("✓ Upload complete")
