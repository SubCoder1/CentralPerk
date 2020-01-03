from whitenoise.storage import CompressedManifestStaticFilesStorage
from storages.backends.s3boto3 import S3Boto3Storage

class WhiteNoiseStaticFilesStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False

class MediaStorage(S3Boto3Storage):    
    location = 'media'    
    file_overwrite = False