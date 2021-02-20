import json
import cgi
import io
import logging
import boto3
import base64
from botocore.client import Config

s3 = boto3.client(
    "s3",
    endpoint_url="http://host.docker.internal:9001/",
    aws_access_key_id="dummy_s3_access_key",
    aws_secret_access_key="dummy_s3_secret_key",
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)


def upload_s3(file_name, field_file_storage):
    try:
        response = s3.put_object(
            Bucket="sample",
            Key=file_name,
            Body=field_file_storage.value,
        )
        return [response, None]
    except Exception as error:
        logging.error(error)
        return [None, error]


def get_file_from_request_body(headers, body):
    fp = io.BytesIO(base64.b64decode(body))
    environ = {"REQUEST_METHOD": "POST"}
    headers = {
        "content-type": headers["Content-Type"],
        "content-length": headers["Content-Length"],
    }

    fs = cgi.FieldStorage(fp=fp, environ=environ, headers=headers)

    try:
        return [fs["file"], None]
    except Exception as error:
        logging.error(error)
        return [None, error]


def lambda_handler(event, context):
    file_item, file_item_error = get_file_from_request_body(
        headers=event["headers"], body=event["body"]
    )

    upload_result, upload_result_error = upload_s3(
        file_name=file_item.filename, field_file_storage=file_item)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "success": True,
        }),
    }
