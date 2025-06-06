import boto3
import json

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('dynamoDBTableName'))

def lambda_handler(event, context):
    try:
        qs_params = event.get('queryStringParameters') or {}
        path_params = event.get('pathParameters') or {}
        image_id = (
            path_params.get('id') or
            qs_params.get('imgId') or
            'platinum.png'
        )

        response = table.get_item(
            Key={
                'image_id': image_id
            }
        )

        item = response.get('Item')

        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'item not found'})
            }

        thumbnail_s3_path = item['thumbnail_path']
        _, _, bucket, *key_parts = thumbnail_s3_path.split("/")
        key = '/'.join(key_parts)

        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': key
            },
            ExpiresIn=1800
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'image_id': image_id,
                'thumbnail_url': presigned_url
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
