"""
Cloud Storage Manager
Supports S3-compatible storage (AWS S3, Cloudflare R2, DigitalOcean Spaces, etc.)

UPDATED January 2025:
- boto3 1.35+ compatibility (Python 3.8 support dropped April 2025)
- Added retry logic for transient failures
- Improved error handling and logging
"""

import os
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from botocore.config import Config
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Retry configuration for transient failures
BOTO_CONFIG = Config(
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'  # Adaptive retry mode (2025 best practice)
    },
    connect_timeout=10,
    read_timeout=30,
    max_pool_connections=25
)


class StorageManager:
    """
    Manages file uploads to S3-compatible storage
    
    Supports:
    - AWS S3
    - Cloudflare R2 (recommended - free egress!)
    - DigitalOcean Spaces
    - Any S3-compatible service
    """
    
    def __init__(
        self,
        bucket_name: str,
        access_key: str,
        secret_key: str,
        endpoint_url: Optional[str] = None,
        region: str = "auto"
    ):
        """
        Initialize storage manager
        
        Args:
            bucket_name: Name of the S3 bucket
            access_key: S3 access key ID
            secret_key: S3 secret access key
            endpoint_url: Custom endpoint (for R2, Spaces, etc.)
            region: AWS region (use 'auto' for Cloudflare R2)
        """
        self.bucket_name = bucket_name
        self.enabled = bool(bucket_name and access_key and secret_key)
        
        if not self.enabled:
            logger.warning("Storage not configured - files will be stored locally (not recommended for production)")
            return
        
        try:
            # Initialize S3 client with retry configuration
            self.s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
                config=BOTO_CONFIG
            )
            
            # Test connection
            self.s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"Storage initialized: {bucket_name}")
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Storage initialization failed: {e}")
            self.enabled = False
    
    def upload_file(self, local_path: str, remote_key: str) -> Optional[str]:
        """
        Upload file to storage
        
        Args:
            local_path: Path to local file
            remote_key: Key/path in bucket (e.g., 'videos/abc123.mp4')
        
        Returns:
            Public URL of uploaded file, or None if failed
        """
        if not self.enabled:
            logger.warning(f"Storage disabled - file not uploaded: {local_path}")
            return None
        
        try:
            # Upload file
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                remote_key,
                ExtraArgs={'ContentType': self._get_content_type(local_path)}
            )
            
            # Generate URL
            url = self._generate_url(remote_key)
            logger.info(f"Uploaded: {remote_key}")
            return url
            
        except ClientError as e:
            logger.error(f"Upload failed: {e}")
            return None
    
    def download_file(self, remote_key: str, local_path: str) -> bool:
        """
        Download file from storage
        
        Args:
            remote_key: Key/path in bucket
            local_path: Where to save locally
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            self.s3_client.download_file(self.bucket_name, remote_key, local_path)
            logger.info(f"Downloaded: {remote_key}")
            return True
        except ClientError as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def delete_file(self, remote_key: str) -> bool:
        """
        Delete file from storage
        
        Args:
            remote_key: Key/path in bucket
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=remote_key)
            logger.info(f"Deleted: {remote_key}")
            return True
        except ClientError as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def generate_presigned_url(self, remote_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate temporary download URL
        
        Args:
            remote_key: Key/path in bucket
            expiration: URL validity in seconds (default 1 hour)
        
        Returns:
            Presigned URL or None if failed
        """
        if not self.enabled:
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': remote_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Presigned URL generation failed: {e}")
            return None
    
    def _generate_url(self, remote_key: str) -> str:
        """Generate public URL for file"""
        if hasattr(self, 's3_client') and self.s3_client._endpoint.host:
            # Custom endpoint (R2, Spaces, etc.)
            endpoint = self.s3_client._endpoint.host
            return f"{endpoint}/{self.bucket_name}/{remote_key}"
        else:
            # AWS S3
            return f"https://{self.bucket_name}.s3.amazonaws.com/{remote_key}"
    
    def _get_content_type(self, filename: str) -> str:
        """Determine content type from filename"""
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
            '.mkv': 'video/x-matroska',
            '.webm': 'video/webm',
        }
        return content_types.get(ext, 'application/octet-stream')


# Singleton instance
_storage_manager: Optional[StorageManager] = None


def init_storage(
    bucket_name: str,
    access_key: str,
    secret_key: str,
    endpoint_url: Optional[str] = None,
    region: str = "auto"
) -> StorageManager:
    """Initialize global storage manager"""
    global _storage_manager
    _storage_manager = StorageManager(bucket_name, access_key, secret_key, endpoint_url, region)
    return _storage_manager


def get_storage() -> Optional[StorageManager]:
    """Get global storage manager instance"""
    return _storage_manager
