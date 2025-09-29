import json
import plotly.graph_objects as go
import npv_logic as npv_l
import uuid
from datetime import datetime
from decimal import Decimal

import boto3
import os

table_name = os.environ.get("DYNAMODB_TABLE")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(table_name)  # nome della tua tabella DynamoDB

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
    return build_response(200, {"message": "Service is operational v8 TEST"})

def save_scenario(event):
    body = json.loads(event["body"])

    # Genera ID scenario univoco
    scenario_id = str(uuid.uuid4())
    
    # Version temporanea: timestamp in secondi (o incrementale se vuoi)
    version = int(datetime.utcnow().timestamp())
    
    # Costruisci la mappa 'years'
    years = {}
    for i in range(1, 6):
        years[str(i)] = {
            "rev": Decimal(str(body.get(f"rev_{i}", 0))),
            "ebitda": Decimal(str(body.get(f"ebitda_{i}", 0))),
            "cpx": Decimal(str(body.get(f"cpx_{i}", 0)))
        }

    wacc = Decimal(str(body.get("wacc", 0)))
    pgr = Decimal(str(body.get("pgr", 0)))
    cf_adv = Decimal(str(body.get("cf_adv", 0)))
    name = str(body.get("scenario_name"))

    # Costruisci l'item
    item = {
        "scenarioid": scenario_id,
        "version": version,
        "name": name,
        "years": years,
        "wacc": wacc,
        "pgr": pgr,
        "cf_adv": cf_adv
    }

    # Inserisci in DynamoDB
    table.put_item(Item=item)
    
    return build_response(200, {
            "message": "Scenario salvato",
            "scenarioid": scenario_id,
            "name": name
        })

def calculate_graph(event):
    # 1. Leggere body dalla richiesta API Gateway
    body = json.loads(event["body"])
    print(body)

    anni = [1, 2, 3, 4, 5]
    varA = [float(body.get(f"rev_{i}") or 0) for i in anni]
    varB = [float(body.get(f"ebitda_{i}") or 0) for i in anni]
    varC = [float(body.get(f"cpx_{i}") or 0) for i in anni]
    wacc = float(body.get("wacc") or 0)
    pgr = float(body.get("pgr") or 0)
    cf_adv = float(body.get("cf_adv") or 0)

    # Grafico 1: Variabile A
    figA = go.Figure()
    figA.add_trace(go.Scatter(x=anni, y=varA, mode="lines+markers", name="Revenue"))
    figA.update_layout(title="Revenue", template="plotly_white")

    # Grafico 2: Variabile B
    figB = go.Figure()
    figB.add_trace(go.Scatter(x=anni, y=varB, mode="lines+markers", name="Ebitda"))
    figB.update_layout(title="Ebitda [percent of rev]", template="plotly_white", yaxis=dict(tickformat=".0%", range=[0, 1]))

    # Grafico 3: Variabile C
    figC = go.Figure()
    figC.add_trace(go.Scatter(x=anni, y=varC, mode="lines+markers", name="Capex"))
    figC.update_layout(title="Capex", template="plotly_white")
    
    npv, tv, cf = npv_l.npv_dcf_pgr(varA, varB, varC, pgr, wacc, cf_adv)
    
    figD = go.Figure()
    figD.add_trace(go.Scatter(x=anni, y=cf, mode="lines+markers", name="Cash Flow"))
    figD.update_layout(title="Cash Flow", template="plotly_white")
    
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


def get_scenarios():

    try:
        # Facciamo uno scan (attenzione su tabelle grandi)
        # puoi sostituire con Query se hai pattern migliore
        scan_kwargs = {}
        items = []
        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs['ExclusiveStartKey'] = start_key
            resp = table.scan(**scan_kwargs)
            items.extend(resp.get("Items", []))
            start_key = resp.get("LastEvaluatedKey", None)
            done = start_key is None

        items = [decimal_to_native(i) for i in items]
        print(items)
        # opzionale: ritornare solo un subset di campi per la lista (es. scenarioid, version, wacc)
        summary = [
            {
                "scenarioid": i["scenarioid"],
                "version": i["version"],
                "wacc": i.get("wacc"),
                "pgr": i.get("pgr"),
                "cf_adv": i.get("cf_adv")
            } for i in items
        ]
        print(summary)
        return build_response(200, {"items": summary})
    except Exception as e:
        return build_response(500, {"message": "errore interno", "error": str(e)})
    
# helper per convertire Decimal -> float/int/string
def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    if isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        # se è intero restituisci int, altrimenti float
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    return obj