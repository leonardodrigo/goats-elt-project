from minio import Minio
from minio.error import S3Error
import logging
import io
import json

logger = logging.getLogger(__name__)


class MinIOClient:
    def __init__(
        self, endpoint: str, access_key: str, secret_key: str, bucket_name: str
    ) -> None:
        self.client = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=False
        )
        self.bucket_name = bucket_name

    def create_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' created successfully")
        else:
            logger.info(f"Bucket '{self.bucket_name}' already exists")

    def upload_json(self, object_name: str, data: dict) -> None:
        try:
            json_data = json.dumps(data, indent=2)
            data_stream = io.BytesIO(json_data.encode("utf-8"))

            self.client.put_object(
                self.bucket_name,
                object_name,
                data_stream,
                length=len(json_data.encode("utf-8")),
                content_type="application/json",
            )
            logger.info(f"Data loaded successfully to {self.bucket_name}/{object_name}")
        except S3Error as e:
            if e.code == "NoSuchBucket":
                logger.warning(
                    f"Bucket {self.bucket_name} does not exist. Creating bucket..."
                )
                self.create_bucket()
                self.upload_json(object_name, data)

    def read_object(self, object_name: str) -> dict:
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read().decode("utf-8")
            return json.loads(data)
        except S3Error as e:
            logger.error(
                f"Error reading object {object_name} from bucket {self.bucket_name}: {e}"
            )
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {}
