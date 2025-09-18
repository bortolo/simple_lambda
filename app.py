import json
import numpy
import pandas
import plotly.express as px
import plotly.graph_objects as go

# Definizione dei path
status_check_path = "/status"
title_path = "/title"
graph_path = "/graph"

def build_response(status_code, body, content_type="application/json"):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": content_type,
            "Access-Control-Allow-Origin": "*"  # Abilitare CORS
        },
        "body": body if isinstance(body, str) else json.dumps(body)
    }

def get_status():
    return build_response(200, {"message": "Service is operational"})

def get_graph(event):
    # 1. Leggere body dalla richiesta API Gateway
    print(event)
    print(event["body"])
    body = json.loads(event["body"])
    print(body)

    anni = [1, 2, 3, 4, 5]
    varA = [float(body.get(f"varA_{i}", 0)) for i in anni]
    varB = [float(body.get(f"varB_{i}", 0)) for i in anni]
    varC = [float(body.get(f"varC_{i}", 0)) for i in anni]

    # Grafico 1: Variabile A
    figA = go.Figure()
    figA.add_trace(go.Scatter(x=anni, y=varA, mode="lines+markers", name="Variabile A"))
    figA.update_layout(title="Variabile A", xaxis_title="Anno", yaxis_title="Valore", template="plotly_white")

    # Grafico 2: Variabile B
    figB = go.Figure()
    figB.add_trace(go.Scatter(x=anni, y=varB, mode="lines+markers", name="Variabile B"))
    figB.update_layout(title="Variabile B", xaxis_title="Anno", yaxis_title="Valore", template="plotly_white")

    # Grafico 3: Variabile C
    figC = go.Figure()
    figC.add_trace(go.Scatter(x=anni, y=varC, mode="lines+markers", name="Variabile C"))
    figC.update_layout(title="Variabile C", xaxis_title="Anno", yaxis_title="Valore", template="plotly_white")

    # Convertire in dict serializzabili
    response = {
        "figA": figA.to_dict(),
        "figB": figB.to_dict(),
        "figC": figC.to_dict()
    }

    # 4. Restituire risposta per API Gateway
    return build_response(
                            200,
                            json.dumps(response),
                            content_type="application/json"
                        )
    
def lambda_handler(event, context):
    print("Request event:", event)

    response = None
    try:
        # http_method = event.get("httpMethod")
        # path = event.get("path")
        context = event.get("requestContext")
        print(context)
        http = context.get("http")
        print(http)
        method = http.get("method")
        path = http.get("path")
        print(method)
        print(path)
        
        # Risposta al preflight (OPTIONS)
        if method == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",                # chi può chiamare (usa * o dominio specifico)
                    "Access-Control-Allow-Methods": "POST, OPTIONS",   # metodi permessi
                    "Access-Control-Allow-Headers": "Content-Type"     # header permessi
                },
                "body": ""
            }
        elif method == "GET" and path == status_check_path:
            response = get_status()
        elif method == "POST" and path == graph_path:
            response = get_graph(event)
        else:
            response = build_response(404, {"error": "Not Found"})

    except Exception as e:
        print("Error:", e)
        response = build_response(500, {"error": "Internal Server Error"})

    return response