import cv2
import numpy as np
import base64
import json

def handle(req):
    data = json.loads(req)
    img = cv2.imdecode(np.frombuffer(base64.b64decode(data["image_base64"]), np.uint8), cv2.IMREAD_COLOR)
    hist = cv2.calcHist([img], [0,1,2], None, [8,8,8], [0,256,0,256,0,256])
    return json.dumps({ "color_histogram": hist.flatten().tolist() })
