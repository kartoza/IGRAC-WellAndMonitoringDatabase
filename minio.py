# coding=utf-8
"""
Utilities for s3.

.. note:: Returning files from s3 bucket.
"""

import os

import s3fs


class S3FileSyetem:
    """Return s3 client."""

    def __init__(self, client, bucket):
        """Return a MinioClient object."""
        self.s3 = s3fs.S3FileSystem(
            key=os.environ.get(f'{client}_S3_ACCESS_KEY', ''),
            secret=os.environ.get(f'{client}_S3_SECRET_KEY', ''),
            endpoint_url=os.environ.get(f'{client}_S3_ENDPOINT_URL', ''),
            client_kwargs={
                'region_name': os.environ.get(
                    f'{client}_S3_REGION_NAME', ''
                )
            }
        )
        self.bucket = bucket

    def open_file(self, filepath):
        """Open and read file."""
        return self.s3.open(
            f's3://{self.bucket}/{filepath}',
            'r',
            encoding="utf8",
            errors='ignore'
        )

    def files(self, folder=None):
        """Lists files in an S3 bucket."""
        if folder:
            files = self.s3.ls(f'{self.bucket}/{folder}')
        else:
            files = self.s3.ls(f'{self.bucket}')
        files.sort()
        return files

    def exist(self, path):
        """Check if path is exist."""
        if path:
            return self.s3.exists(f'{self.bucket}/{path}')
        else:
            return True
