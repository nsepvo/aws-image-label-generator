import json
import boto3

# Configuration 
# S3 bucket where images are stored
BUCKET = "image-label-generator-nevenspooner"

# AWS region 
REGION = "ap-southeast-2"

# AWS Clients
# Added endpoint_url to force correct regional S3 routing
# This prevents 307 redirects and presigned URL issues
s3 = boto3.client(
    "s3",
    region_name=REGION,
    endpoint_url=f"https://s3.{REGION}.amazonaws.com"
)

# Rekognition client used for image label detection
rekognition = boto3.client("rekognition", region_name=REGION)


# Main lambda function 
def lambda_handler(event, context):

    # Log incoming request for debugging in CloudWatch
    print("EVENT RECEIVED:", json.dumps(event))

    try:
        # Parse request body
        body = event.get("body")

        # API Gateway sends body as string which is converted to dict
        if body:
            body = json.loads(body)
        else:
            body = {}

        # Determine what the frontend wants to do
        action = body.get("action")

        # 1. Generate presigned upload URL 
        if action == "getUploadUrl":

            # File name coming from frontend
            file_name = body["fileName"]

            # Content type (image/jpeg, image/png, etc.)
            content_type = body.get("contentType", "image/jpeg")

            print("Generating presigned URL for:", file_name)

            # Create a temporary signed URL allowing browser to upload directly to S3
            upload_url = s3.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": BUCKET,
                    "Key": file_name,
                    "ContentType": content_type
                },
                ExpiresIn=300,   # URL valid for 5 minutes
                HttpMethod="PUT"
            )

            print("PRESIGNED URL:", upload_url)
            print("UPLOAD URL GENERATED")

            # Return upload URL to frontend
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "content-type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": json.dumps({
                    "uploadUrl": upload_url,
                    "fileName": file_name
                })
            }

        # 2. Analyse image using Rekognition
        if action == "analyse":

            # S3 object key (file name in bucket)
            key = body["key"]

            print("Analysing image:", key)

            # Send image to AWS Rekognition for label detection
            response = rekognition.detect_labels(
                Image={
                    "S3Object": {
                        "Bucket": BUCKET,
                        "Name": key
                    }
                },
                MaxLabels=10,
                MinConfidence=80
            )

            # Format Rekognition response into clean JSON
            labels = [
                {
                    "name": l["Name"],
                    "confidence": round(l["Confidence"], 2)
                }
                for l in response["Labels"]
            ]

            print("REKOGNITION RESULT:", labels)

            # Return labels to frontend
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "content-type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": json.dumps({
                    "labels": labels
                })
            }

        # Invalid action handler
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid action"})
        }

    except Exception as e:

        # Log full error in CloudWatch
        print("ERROR:", str(e))

        # Return error response to frontend
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }
