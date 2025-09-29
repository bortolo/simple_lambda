import utils as ut
import api_logic as api

# Definizione dei path
status_check_path = "/status"
graph_path = "/graph"
save_path = "/save"

def lambda_handler(event, context):
    response = None
    try:
        method, path = ut.http_version_handler(event)
        print(method)
        print(path)        
        if method is None or path is None :
            return api.build_response(400, f"Unsupported HTTP version: {event.get('version')}", content_type="text/plain")
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
            response = api.get_status()
        elif method == "POST" and path == graph_path:
            response = api.calculate_graph(event)
        elif method == "POST" and path == save_path:
            response = api.save_scenario(event)
        else:
            response = api.build_response(404, {"error": "Not Found"})

    except Exception as e:
        print("Error:", e)
        response = api.build_response(500, {"error": "Internal Server Error"})

    return response