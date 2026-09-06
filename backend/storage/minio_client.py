import os

from dotenv import load_dotenv
from minio import Minio


load_dotenv()


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "polarconnect")


if not MINIO_ENDPOINT:
    raise RuntimeError("MINIO_ENDPOINT is not set in .env")

if not MINIO_ACCESS_KEY:
    raise RuntimeError("MINIO_ACCESS_KEY is not set in .env")

if not MINIO_SECRET_KEY:
    raise RuntimeError("MINIO_SECRET_KEY is not set in .env")


client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# ============================================================
# CREATE BUCKET
# ============================================================

def create_bucket_if_not_exists():

    try:

        if not client.bucket_exists(MINIO_BUCKET):

            client.make_bucket(MINIO_BUCKET)

            print(
                f"Bucket '{MINIO_BUCKET}' created"
            )

        else:

            print(
                f"Bucket '{MINIO_BUCKET}' already exists"
            )

    except Exception as e:

        raise RuntimeError(
            f"MinIO connection failed: {str(e)}"
        )