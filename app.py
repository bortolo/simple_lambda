import json
import plotly.express as px

def lambda_handler(event, context):
    # genera un grafico semplice
    fig = px.line(x=[1, 2, 3], y=[4, 5, 6], title="Grafico da Lambda")
    html_div = fig.to_html(full_html=True)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html"
        },
        "body": html_div
    }
