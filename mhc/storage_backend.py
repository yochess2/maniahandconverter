from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class HhStorage(S3Boto3Storage):
    location = settings.AWS_HH_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False

class JsonStorage(S3Boto3Storage):
    location = settings.AWS_JSON_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
