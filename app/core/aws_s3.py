import aioboto3
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastapi import UploadFile, HTTPException

from app.core.config import settings

load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,

)
BUCKET_NAME = settings.AWS_S3_BUCKET


def upload_file_to_s3(file: UploadFile, bill_id: str, folder: str = "bills") -> str:
    """Upload image to S3 as <folder>/<bill_id>.<ext> and return key."""
    ext = file.filename.split(".")[-1]
    key = f"{folder}/{bill_id}.{ext}"

    try:
        s3.upload_fileobj(
            file.file,
            BUCKET_NAME,
            key,
            ExtraArgs={"ContentType": file.content_type},
        )
        return key
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 upload error: {e}")


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    """Generate temporary download URL."""
    try:
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": key},
            ExpiresIn=expires_in,
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 presign error: {e}")


async def delete_file_from_s3_async(file_url: str):
    """Delete file from S3 asynchronously"""
    if not file_url:
        return
    bucket = settings.AWS_S3_BUCKET
    key = file_url.split(f"{bucket}/")[-1]

    session = aioboto3.Session()
    async with session.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
    ) as s3:
        await s3.delete_object(Bucket=bucket, Key=key)
