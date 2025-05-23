Add file ▸ Create new file
File name: scripts/deploy.py
import boto3, mimetypes, os, pathlib

s3 = boto3.client("s3", region_name=os.environ["REGION"])
bucket = os.environ["BUCKET"]
root = pathlib.Path("site")

for file in root.rglob("*"):
    if file.is_file():
        ctype, _ = mimetypes.guess_type(file.name)
        s3.upload_file(
            str(file), bucket, str(file.relative_to(root)),
            ExtraArgs={"ContentType": ctype or "text/plain",
                       "ACL": "public-read"}
        )
print("▲ Upload complete")
