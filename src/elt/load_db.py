import boto3
import json
import psycopg2
from datetime import datetime

# ==== MinIO / S3 settings ====
endpoint = "http://localhost:9000"
access_key = "myuser"
secret_key = "mypassword"
bucket = "test"

s3 = boto3.client(
    "s3",
    endpoint_url=endpoint,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)

def read_file(key: str):
    response = s3.get_object(Bucket=bucket, Key=key)
    return response["Body"].read().decode("utf-8")


# ==== Postgres settings ====
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="goats_elt",
    user="myuser",
    password="mypassword"
)
cursor = conn.cursor()


# ==== Create table if not exists ====
cursor.execute("""
    CREATE TABLE IF NOT EXISTS spotify_plays_raw (
        raw_json_item JSONB NOT NULL,
        run_timestamp TIMESTAMPTZ NOT NULL
    );
""")
conn.commit()


# ==== Read MOST RECENT file from S3 ====
objects = s3.list_objects_v2(Bucket=bucket)

if "Contents" not in objects:
    print("Bucket is empty.")
else:
    # most_recent = sorted(
    #     objects["Contents"],
    #     key=lambda x: x["LastModified"],
    #     reverse=True
    # )[0]
    #
    # key = most_recent["Key"]
    # print(f"\n--- Reading most recent file: {key} ---")

    file_contents = read_file("test.json")
    run_timestamp = datetime.now()

    # Parse JSON
    data = json.loads(file_contents)

    # Extract items list
    items = data.get("items", [])

    # Insert one row per Spotify item
    for item in items:
        raw_json_item = json.dumps(item)

        cursor.execute(
            """
            INSERT INTO spotify_plays_raw (raw_json_item, run_timestamp)
            VALUES (%s, %s)
            """,
            (raw_json_item, run_timestamp)
        )

        conn.commit()

cursor.close()
conn.close()
