## AWS Resources Setup

- Create **two S3 buckets**:  
  - One for original uploads  
  - One for generated thumbnails  
- Create a **DynamoDB table** (e.g. `PhotoMetadata`)
- Replace `<bucket-name>`, `<region>`, `<accountId>`, and `<TableName>` in IAM policy templates
- Create **two IAM policies**:
  - One for the thumbnail Lambda (S3 Get/Put, DynamoDB Put, CloudWatch)
  - One for the API Gateway Lambda (S3 Get, DynamoDB Get/Scan, CloudWatch)
- Create **IAM roles** for each Lambda and attach the corresponding policy

---

## Thumbnail Lambda Setup

- Create the Lambda function (Python)
- Assign the thumbnail execution role
- Set up an **S3 trigger** for "ObjectCreated" events
- Add a **Lambda layer** with Pillow (use one from [Klayers](https://github.com/keithrozario/Klayers))
- Add environment variables:  
  - `dynamoDBTableName`  
  - `thumbnail_bucket`  

---

## API Gateway Lambda Setup

- Create the Lambda function for API access
- Assign the API Gateway execution role
- Add environment variable:  
  - `dynamoDBTableName`

---

## API Gateway Setup

- Create a **REST API** in API Gateway
- Create a **resource** (e.g. `/thumbnails`)
- Create a **GET method**:
  - Enable **Lambda Proxy Integration**
  - Add **query string parameter** `imgId` (optional, but helps with UI)
  - Attach it to the gateway Lambda
- Deploy the API to a new **stage** (e.g. `prod`)
- Use the **Invoke URL** + stage/resource path to access it: (e.g. `https://<api-id>.execute-api.<region>.amazonaws.com/prod/thumbnails?imgId=example.jpg`)

---

## Testing

- Test by uploading an image to the **original upload bucket**, it should create a 200x200 thumbnail in the **thumbnail bucket**
- You can also test the thumbnail lambda manually by creating a test event using the following JSON (replace bucket and key with your values). Make sure the object already exist in the bucket before testing:
  ```json
  {
    "Records": [
      {
        "eventVersion": "2.0",
        "eventSource": "aws:s3",
        "awsRegion": "your-region",
        "eventTime": "1970-01-01T00:00:00.000Z",
        "eventName": "ObjectCreated:Put",
        "userIdentity": {
          "principalId": "EXAMPLE"
        },
        "requestParameters": {
          "sourceIPAddress": "127.0.0.1"
        },
        "responseElements": {
          "x-amz-request-id": "EXAMPLE123456789",
          "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
        },
        "s3": {
          "s3SchemaVersion": "1.0",
          "configurationId": "testConfigRule",
          "bucket": {
            "name": "your-original-bucket-name",
            "ownerIdentity": {
              "principalId": "EXAMPLE"
            },
            "arn": "arn:aws:s3:::your-original-bucket-name"
          },
          "object": {
            "key": "object-name.png",
            "size": 1024,
            "eTag": "0123456789abcdef0123456789abcdef",
            "sequencer": "0A1B2C3D4E5F678901"
          }
        }
      }
    ]
  }
