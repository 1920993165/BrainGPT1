from diffusers import DiffusionPipeline
import torch
from PIL import Image
import numpy as np

pipe = DiffusionPipeline.from_pretrained("stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
pipe.to("cuda")

# if using torch < 2.0
# pipe.enable_xformers_memory_efficient_attention()

prompt = "An astronaut riding a green horse"

prompt = "一个有翅膀的大象"

images = pipe(prompt=prompt).images

# Get the first generated image from the list
generated_image = images[0]

# Convert the PIL Image to a numpy array
generated_array = np.array(generated_image)

# Create a PIL image from the numpy array
pil_image = Image.fromarray(generated_array)

# Choose save path and file name
save_path = prompt + ".png"

# Save the image locally
pil_image.save(save_path)

print(f"Generated image saved to: {save_path}")


