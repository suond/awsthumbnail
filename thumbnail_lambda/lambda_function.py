import boto3
import botocore
import urllib.parse
import os
import time
from PIL import Image

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('dynamoDBTableName'))


def lambda_handler(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

        download_path = f"/tmp/{os.path.basename(key)}"
        upload_key = f"thumbnails/{os.path.basename(key)}"
        upload_path = f"/tmp/thumbnail_{os.path.basename(key)}"
        thumbnail_bucket = os.environ.get('thumbnail_bucket')

        print(f"Downloading: s3://{bucket}/{key}")
        s3.download_file(bucket, key, download_path)

        print("Processing image...")
        with Image.open(download_path) as img:
            img.thumbnail((200, 200), Image.BOX)
            img.save(upload_path)

        print(f"Uploading thumbnail to: s3://{thumbnail_bucket}/{upload_key}")
        s3.upload_file(upload_path, thumbnail_bucket, upload_key)

        print("Writing metadata to DynamoDB")
        table.put_item(
            Item={
                'image_id': key,
                'thumbnail_path': f"s3://{thumbnail_bucket}/{upload_key}",
                'created_at': int(time.time())
            }
        )

        return {
            'statusCode': 200,
            'body': f'Thumbnail created for {key}'
        }

    except Exception as e:
        print(f"Error processing file: {e}")
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
