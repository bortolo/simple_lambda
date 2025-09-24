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
    body = json.loads(event["body"])
    print(body)

    anni = [1, 2, 3, 4, 5]
    varA = [float(body.get(f"rev_{i}", 0)) for i in anni]
    varB = [float(body.get(f"ebitda_{i}", 0)) for i in anni]
    varC = [float(body.get(f"cpx_{i}", 0)) for i in anni]
    wacc = float(body.get("wacc") or 0)
    pgr = float(body.get("pgr") or 0)
    cf_adv = float(body.get("cf_adv") or 0)

    # Grafico 1: Variabile A
    figA = go.Figure()
    figA.add_trace(go.Scatter(x=anni, y=varA, mode="lines+markers", name="Revenue"))
    figA.update_layout(title="Revenue", xaxis_title="Anno", yaxis_title="Valore", template="plotly_white")

    # Grafico 2: Variabile B
    figB = go.Figure()
    figB.add_trace(go.Scatter(x=anni, y=varB, mode="lines+markers", name="Ebitda"))
    figB.update_layout(title="Ebitda [percent of rev]", xaxis_title="Anno", yaxis_title="Valore", template="plotly_white")

    # Grafico 3: Variabile C
    figC = go.Figure()
    figC.add_trace(go.Scatter(x=anni, y=varC, mode="lines+markers", name="Capex"))
    figC.update_layout(title="Capex", xaxis_title="Anno", yaxis_title="Valore", template="plotly_white")
    
    npv, tv, cf = npv_dcf_pgr(varA, varB, varC, pgr, wacc, cf_adv)
    
    figD = go.Figure()
    figD.add_trace(go.Scatter(x=anni, y=cf, mode="lines+markers", name="Cash Flow"))
    figD.update_layout(title="Cash Flow", xaxis_title="Anno", yaxis_title="Valore", template="plotly_white")
    
    # Convertire in dict serializzabili
    response = {
        "figA": figA.to_dict(),
        "figB": figB.to_dict(),
        "figC": figC.to_dict(),
        "figD": figD.to_dict(),
        "npv": npv, 
        "tv": tv
    }

    # 4. Restituire risposta per API Gateway
    return build_response(
                            200,
                            json.dumps(response),
                            content_type="application/json"
                        )

def npv_dcf_pgr(revenue, ebitda, capex, pgr, wacc, cash_adv):
    years = len(revenue)
    cash_flows = []
    
    for t in range(1, years + 1):
        cf = (revenue[t-1] * ebitda[t-1] - capex[t-1])*(1 - 0.28)
        cash_flows.append(cf / (1 + wacc)**(t-cash_adv))
    
    # Terminal value
    terminal_value = (cash_flows[-1] * (1 + pgr)) / (wacc - pgr)
    
    npv = sum(cash_flows) + terminal_value
    
    return npv, terminal_value, cash_flows

def http_version_handler(event):
    """
    Restituisce (method, path) a seconda della versione dell'evento.
    Ritorna (None, None) se la versione non è supportata.
    """
    method, path = None, None
    version = event.get("version")
    if version == "2.0" :
        context = event.get("requestContext")
        http = context.get("http")
        method = http.get("method")
        path = http.get("path")
    elif version == "1.0" :
        method = event.get("httpMethod")
        path = event.get("resource")
    elif version == None :
        print("[ATTENZIONE] non esiste il parmetro version, ipotizziamo chiamata API AWS da REST GW")
        method = event.get("httpMethod")
        path = event.get("path")
    return method, path

def lambda_handler(event, context):
    print("Request event:", event)

    response = None
    try:
        
        method, path = http_version_handler(event)
        print(method)
        print(path)        
        if method is None or path is None :
            return build_response(400, f"Unsupported HTTP version: {event.get('version')}", content_type="text/plain")
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