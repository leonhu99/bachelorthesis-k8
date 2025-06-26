import requests
import json

def handle(req):
    payload = json.loads(req)
    res = requests.post("http://internal-api.default.svc.cluster.local/store", json=payload) # Adjust URL to the internal API endpoint to actually store the result
    return json.dumps({ "status": res.status_code })
