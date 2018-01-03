from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class PrivateUnconvertedStorage(S3Boto3Storage):
    location = settings.AWS_PRIVATE_UNCONVERTED_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False

class PrivateJsonStorage(S3Boto3Storage):
    location = settings.AWS_PRIVATE_UNCONVERTED_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
