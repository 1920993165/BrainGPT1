from flask import Flask, request, jsonify
from diffusers import DiffusionPipeline
import torch
from PIL import Image
import numpy as np
import io

app = Flask(__name__)

# Initialize DiffusionPipeline
pipe = DiffusionPipeline.from_pretrained("../../Models/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
pipe.to("cuda")

# Define an API endpoint to generate images
@app.route('/generate_image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt', '')

    # Generate images
    images = pipe(prompt=prompt).images
    generated_image = images[0]

    # Convert the PIL Image to a numpy array
    generated_array = np.array(generated_image)

    # Create a PIL image from the numpy array
    pil_image = Image.fromarray(generated_array)

    # Convert PIL image to bytes
    img_byte_array = io.BytesIO()
    pil_image.save(img_byte_array, format='PNG')
    img_byte_array.seek(0)

    return img_byte_array.getvalue(), 200, {'Content-Type': 'image/png'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6002)
