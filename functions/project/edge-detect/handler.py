import cv2
import numpy as np
import base64
import json

def handle(req):
    data = json.loads(req)
    img = cv2.imdecode(np.frombuffer(base64.b64decode(data["image_base64"]), np.uint8), cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(img, 100, 200)
    _, buffer = cv2.imencode('.jpg', edges)
    return json.dumps({ "edges_base64": base64.b64encode(buffer).decode() })
