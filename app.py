import json
import plotly.express as px

def lambda_handler(event, context):
    # dati di esempio
    x = [1, 2, 3]
    y = [4, 5, 6]

    fig = px.line(x=x, y=y, title="Grafico Plotly da Lambda")
    
    # converto in HTML (solo il div)
    html_div = fig.to_html(full_html=False)
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"graph": html_div})
    }
