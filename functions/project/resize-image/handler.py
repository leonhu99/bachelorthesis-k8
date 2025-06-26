import cv2
import numpy as np
import base64
import json

def handle(req):
    data = json.loads(req)
    image_b64 = data.get("image_base64")
    img = cv2.imdecode(np.frombuffer(base64.b64decode(image_b64), np.uint8), cv2.IMREAD_COLOR)
    resized = cv2.resize(img, (256, 256))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    _, buffer = cv2.imencode('.jpg', gray)
    return json.dumps({ "image_base64": base64.b64encode(buffer).decode() })
