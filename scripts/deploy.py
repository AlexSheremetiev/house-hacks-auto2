import boto3, mimetypes, os, pathlib

s3 = boto3.client(
    "s3",
    region_name=os.getenv("REGION"),
    endpoint_url="https://storage.yandexcloud.net"
)

bucket = os.environ["BUCKET"]
root   = pathlib.Path("site")

for file in root.rglob("*"):
    if file.is_file():
        # ---------- единственная правка ----------
        ctype = "text/html" if file.suffix == ".html" else (
            "application/rss+xml" if file.name == "feed.xml" else
            mimetypes.guess_type(file.name)[0] or "text/plain"
        )

        s3.upload_file(
            str(file), bucket, str(file.relative_to(root)),
            ExtraArgs={"ContentType": ctype, "ACL": "public-read"},
        )

print("✓ Upload complete")
