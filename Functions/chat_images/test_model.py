import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')
import argparse
import torch
from transformers import AutoModel, AutoTokenizer

torch.set_grad_enabled(False)

parser = argparse.ArgumentParser()
parser.add_argument("--num_gpus", default=1, type=int)
parser.add_argument("--dtype", default='fp16', type=str)
args = parser.parse_args()
model_path='../../Models/internlm-xcomposer2-4khd-7b'
# init model and tokenizer
model = AutoModel.from_pretrained(model_path, trust_remote_code=True).eval()



tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

text = '<ImageHere>Please describe this image in detail.'
image = 'test.jpg'
with torch.cuda.amp.autocast():
    with torch.no_grad():
        response, his = model.chat(tokenizer, query=text, image=image, history=[], do_sample=False)
print(response)
print(his)
# The image features a quote by Oscar Wilde, "Live life with no excuses, travel with no regret,"
# set against a backdrop of a breathtaking sunset. The sky is painted in hues of pink and orange,
# creating a serene atmosphere. Two silhouetted figures stand on a cliff, overlooking the horizon.
# They appear to be hiking or exploring, embodying the essence of the quote.
# The overall scene conveys a sense of adventure and freedom, encouraging viewers to embrace life without hesitation or regrets.