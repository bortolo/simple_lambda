import json
import numpy
import pandas
import plotly.express as px
# import plotly.express as px

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
    return build_response(200, {"message": "Service is operational, DOPPIO WOW"})

def get_title():
    return build_response(200, {"title": "Titolo aggiornato dalla Lambda!"})

# def get_graph():
#     df = px.data.iris()
#     fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
#     graph_html = fig.to_json()
#     return build_response(200, graph_html, content_type="application/json")

def get_graph():
    df = px.data.iris()
    fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
    # Converti in dict Python
    fig_dict = fig.to_dict()

    return build_response(
                            200,
                            json.dumps({
                                "data": fig_dict["data"],
                                "layout": fig_dict["layout"]
                            }),
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
        if method == "GET" and path == status_check_path:
            response = get_status()
        elif method == "GET" and path == title_path:
            response = get_title()
        elif method == "GET" and path == graph_path:
            response = get_graph()
        else:
            response = build_response(404, {"error": "Not Found"})

    except Exception as e:
        print("Error:", e)
        response = build_response(500, {"error": "Internal Server Error"})

    return response