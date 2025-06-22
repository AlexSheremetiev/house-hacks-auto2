import boto3, mimetypes, os, pathlib

# —––  Настройка клиента Object Storage  ––––––––––––––––––––––
s3 = boto3.client(
    "s3",
    region_name=os.getenv("REGION"),
    endpoint_url="https://storage.yandexcloud.net",
)

bucket = os.environ["BUCKET"]          # имя бакета из Secrets
root   = pathlib.Path("site")          # папка, которую заливаем

# —––  Проходим по всем файлам внутри site/  ––––––––––––––––––
for file in root.rglob("*"):
    if file.is_file():

        # -------- корректно задаём Content-Type ---------------
        if file.name == "feed.xml":
            ctype = "application/rss+xml; charset=utf-8"
        elif file.suffix == ".html":
            ctype = "text/html; charset=utf-8"
        else:
            # берём из mimetypes, либо fallback на text/plain
            ctype = mimetypes.guess_type(file.name)[0] or "text/plain"

        # -------- загрузка в Object Storage -------------------
        s3.upload_file(
            str(file),                        # локальный путь
            bucket,                           # бакет
            str(file.relative_to(root)),      # ключ (относительный путь)
            ExtraArgs={
                "ContentType": ctype,
                "ACL": "public-read",         # делаем файл публичным
            },
        )

print("✓ Upload complete")
