import requests
from PIL import Image
from io import BytesIO

url = 'http://10.36.0.11:5000/generate_image'

data = {
    "prompt": "An astronaut riding a green horse"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    # Convert the response content to a PIL image
    pil_image = Image.open(BytesIO(response.content))
    pil_image.show()
else:
    print("Request failed with status code:", response.status_code)
