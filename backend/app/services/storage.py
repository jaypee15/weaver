"""
Google Cloud Storage service using S3-compatible API with HMAC keys
"""
import boto3
from botocore.exceptions import ClientError
from app.config import settings


class StorageService:
    """Singleton-like storage service for GCS operations"""
    
    _client = None
    
    @classmethod
    def get_client(cls):
        """Get or create boto3 S3 client for GCS"""
        if cls._client is None:
            cls._client = boto3.client(
                's3',
                endpoint_url='https://storage.googleapis.com',
                aws_access_key_id=settings.GCS_ACCESS_KEY,
                aws_secret_access_key=settings.GCS_SECRET_KEY,
                region_name='auto'
            )
        return cls._client
    
    @classmethod
    def upload_file(cls, bucket_name: str, key: str, content: bytes, content_type: str = None) -> None:
        """Upload a file to GCS"""
        try:
            client = cls.get_client()
            client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type or 'application/octet-stream'
            )
        except ClientError as e:
            raise ValueError(f"Failed to upload to GCS: {str(e)}")
    
    @classmethod
    def download_file(cls, bucket_name: str, key: str) -> bytes:
        """Download a file from GCS"""
        try:
            client = cls.get_client()
            response = client.get_object(Bucket=bucket_name, Key=key)
            return response['Body'].read()
        except ClientError as e:
            raise ValueError(f"Failed to download from GCS: {str(e)}")
    
    @classmethod
    def delete_file(cls, bucket_name: str, key: str) -> None:
        """Delete a file from GCS"""
        try:
            client = cls.get_client()
            client.delete_object(Bucket=bucket_name, Key=key)
        except ClientError as e:
            raise ValueError(f"Failed to delete from GCS: {str(e)}")

