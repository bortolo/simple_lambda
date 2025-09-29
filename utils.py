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