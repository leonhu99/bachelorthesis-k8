import json

def handle(req):
    data = json.loads(req)
    return json.dumps({
        "merged": {
            "edge": data.get("edges_base64"),
            "color": data.get("color_histogram")
        }
    })
