from flask import Flask, render_template, request, jsonify


#from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import AutoTokenizer,AutoModelWithLMHead,AutoModelForCausalLM
import torch

from flask import Flask, render_template, request, jsonify


#from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import AutoTokenizer,AutoModelWithLMHead,AutoModelForCausalLM
import torch

from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)

import json
import os
#from pprint import pprint
#import bitsandbytes as bnb
import torch
import torch.nn as nn
#import transformers
#from datasets import load_dataset
#from huggingface_hub import notebook_login
from peft import (
    LoraConfig,
    PeftConfig,
    PeftModel,
    get_peft_model,
    prepare_model_for_kbit_training
)

#tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
#model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
"""
model_name = 'microsoft/DialoGPT-medium'#'PygmalionAI/pygmalion-6b' #'facebook/blenderbot-400M-distill' #'microsoft/DialoGPT-medium'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
"""

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

'''
model_name = 'microsoft/DialoGPT-medium'#microsoft/DialoGPT-medium'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
'''

PEFT_MODEL = "Sanjeven/chefandrew"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

device_map = {
    "transformer.word_embeddings": 0,
    "transformer.word_embeddings_layernorm": 0,
    "lm_head": "gpu",
    "transformer.h": 0,
    "transformer.ln_f": 0,
}

config = PeftConfig.from_pretrained(PEFT_MODEL)
model = AutoModelForCausalLM.from_pretrained(
    config.base_model_name_or_path,
    return_dict=True,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

tokenizer=AutoTokenizer.from_pretrained(config.base_model_name_or_path)
tokenizer.pad_token = tokenizer.eos_token

model = PeftModel.from_pretrained(model, PEFT_MODEL)

generation_config = model.generation_config
generation_config.max_new_tokens = 200
generation_config.temperature = 0.7
generation_config.top_p = 0.7
generation_config.num_return_sequences = 1
generation_config.pad_token_id = tokenizer.eos_token_id
generation_config.eos_token_id = tokenizer.eos_token_id

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/home")
def home():
    return render_template('chat.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    return get_Chat_response(input)

@app.route("/share", methods=["GET", "POST"])
def share_on_whatsapp():
    global last_reply
    # Message to be shared
    message = last_reply
    
    # WhatsApp URL with pre-defined message
    whatsapp_url = f"https://api.whatsapp.com/send?text={message}"
    
    return render_template('share.html', whatsapp_url=whatsapp_url)

@app.route('/generate_file')
def generate_file():
    global last_reply
    file_content = last_reply
    file_content = file_content.replace("*", " ")
    file_content = file_content.replace("_", " ")
    file_content = file_content.replace("%0a", "\n")
    return file_content

def get_Chat_response(text):
    global last_reply
    device = "cuda:0"

    # <human>: you are a chef, come up with a cooking directions for {}
    #Recipe with
    prompt = """
    <human>: you are a chef, come up with a cooking directions for {}
    <assistant>:
    """.format(text)
    
    prompt = prompt.strip()
    
    #prompt = text

    encoding = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.inference_mode():
        outputs = model.generate(
            input_ids = encoding.input_ids,
            attention_mask = encoding.attention_mask,
            generation_config = generation_config
        )

    print ("ORIGINAL")
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))
    output = (tokenizer.decode(outputs[0], skip_special_tokens=True)).strip()
    print ("OUTPUT STRIPPED")
    print (output)
    modified_string = output.replace('<assistant>:', "")
    modified_string = modified_string.replace('<human>:', "")
    modified_string = modified_string.replace(text, "")
    modified_string = modified_string.replace('you are a chef, come up with a cooking directions for', "")
    modified_string = modified_string.replace('Recipe with', "")
    #modified_string = modified_string.replace(". ", ".\n")
    modified_string = modified_string.replace("User", "")
    print ("REPLACED")
    print (modified_string)
    last_reply = modified_string
    #output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return modified_string
    # Let's chat for 5 lines
    """
    for step in range(5):
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')

        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

        # generated a response while limiting the total chat history to 1000 tokens, 
        chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

        # pretty print last ouput tokens from bot
        return tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    """
    
    
if __name__ == '__main__':
    app.run()
