import json

# import easyocr
# import numpy as np
import requests

# from pathlib import Path


# from PIL import Image

# import psutil

files = {"file": open("samples/sample_urls.jpg", "rb")}

r = requests.post("http://localhost:8000/ocr", files=files)
# r = requests.post("https://fastapi-easyocr.herokuapp.com/ocr", files=files)
print(r.json())
open("response_heroku.json", "w").write(json.dumps(r.json()))
# raw_image = Image.open("samples/sample_urls.jpg").convert("RGB")
# # raw_image.save("WTF2.png")
# image = np.asarray(raw_image)
# print("pre")
# ocr = easyocr.Reader(["en"], gpu=False)
# print("loaded")
# # psutil.Process().memory_info().rss / (1024 * 1024)
# res = ocr.readtext(image)
# print("done")
# print(res)
# print(psutil.Process().memory_info().rss / (1024 * 1024))
