def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/plain",
            "Access-Control-Allow-Origin": "*"
        },
        "body": "Hello from Lambda NEW!"
    }
