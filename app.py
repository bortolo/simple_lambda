import json
import plotly.express as px

def lambda_handler(event, context):
    body = json.loads(event["body"])
    x = body.get("x", [])
    y = body.get("y", [])
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Grafico ricevuto", "x": x, "y": y})
    }
