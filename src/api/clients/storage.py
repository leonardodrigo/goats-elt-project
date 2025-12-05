import logging
import json
from google.cloud import storage
import os

logger = logging.getLogger(__name__)

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

class CloudStorageClient:
    def __init__(self):
        self.project_id = GCP_PROJECT_ID
        self.client = storage.Client(project=self.project_id)

    def upload_json(self, bucket_name, blob_name, data):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        json_data = json.dumps(data)

        blob.upload_from_string(
            json_data,
            content_type="application/json"
        )

        logger.info(f"Uploaded JSON to gs://{bucket_name}/{blob_name}")
        return True

    def download_json(self, bucket_name, blob_name):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        json_data = blob.download_as_text()
        return json.loads(json_data)

    def get_most_recent_gcs_object(self, bucket_name: str):
        bucket = self.client.bucket(bucket_name)
        blobs = list(bucket.list_blobs())
        if not blobs:
            return None
        latest_blob = max(blobs, key=lambda b: b.updated)
        return latest_blob.name

