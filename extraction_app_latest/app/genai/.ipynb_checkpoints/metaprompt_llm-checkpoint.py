import pandas as pd
import torch
import torch.nn.functional as F
import os
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from .genai_meta_prompting import generate_text, construct_meta_prompt
#from .generative_ai_dynamic import generative_ai_dynamic_prompting
from .generative_ai_dynamic_prompting import generative_ai_dynamic_prompting
import re


import google.generativeai as genai
import requests
from langchain_openai import ChatOpenAI  
import json
import requests
import os
import re

api_key="sk-FKC6gCdNdv6akNQYeTv1zw"
base_url="https://genai-sharedservice-apac.pwcinternal.com/"


# === Global cache for model/tokenizer ===
model_cache = {
    "current_model_name": None,
    "tokenizer": None,
    "model": None
}

def get_model_path(component_name: str) -> str:
    """
    Get model path based on the component name.
    """
    if component_name == "llama":
        return r"/data/digitalworkmate/models/llama3.1_instruct"
    elif component_name == "phi-4":
        return r"/data/digitalworkmate/models/Phi4"
    else:
        raise ValueError(f"Unsupported component name: {component_name}")

def load_model_and_tokenizer(model_name: str):
    """
    Load tokenizer and quantized model with caching support.
    If model is already loaded, reuse it.
    If a different model is requested, unload and reload.
    """
    global model_cache

    if model_cache["current_model_name"] == model_name:
        #print(f"Reusing cached model: {model_name}")
        return model_cache["tokenizer"], model_cache["model"]

    # Unload previous model if any
    if model_cache["model"] is not None:
        #print(f"Unloading previous model: {model_cache['current_model_name']}")
        del model_cache["model"]
        del model_cache["tokenizer"]
        torch.cuda.empty_cache()

    #print(f"Loading new model: {model_name}")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        quantization_config=bnb_config
    )
    model.config.use_cache = False

    # Update cache
    model_cache.update({
        "current_model_name": model_name,
        "tokenizer": tokenizer,
        "model": model
    })

    return tokenizer, model

def clean_response(data):
    try:
        json_data=""
        json_match = re.search(r'\{.*\}', data, re.DOTALL)
        try:
            if json_match:
                json_data = json_match.group(0)
            data = json.loads(json_data)
            pretty_json = json.dumps(data, indent=4)
        except json.JSONDecodeError as e:
            #print("Invalid JSON:", e)
            return ""
        return data
    except Exception as e:
            #print("Error in clean_response:", e)
            return ""

# def create_prompt(json_data, model_path, system_message: str, input_message: str, text_data: str) -> dict:
#     """
#     Create the prompt string from the system and user message, then parse it into JSON format.
#     """
#     content = construct_meta_prompt(input_message, system_message, json_data)

#     tokenizer, model = load_model_and_tokenizer(model_path)
#     raw_output = generate_text(tokenizer, model, content, max_new_tokens=1500, temp=0.1)

#     # === Step 1: Strip markdown formatting and trailing quotes ===
#     cleaned_output = clean_response(raw_output)
    

#     # Remove markdown code block if exists
   
#     return cleaned_output

    
def generate_response(
    config_data: dict,
    text_file_path: str,
    output_file_path: str = "invoice_llm_response.txt",
    max_new_tokens: int = 1500
) -> dict:
    """
    Generate a response from the AI model using invoice data and a JSON config.
    
    Parameters:
    - config_data: dict - Loaded configuration from JSON.
    - text_file_path: str - Path to the invoice .txt file.
    - output_file_path: str - File to save the generated response.
    - max_new_tokens: int - Maximum number of tokens to generate.

    Returns:
    - dict: The generated response (structured as JSON).
    """

    # Load invoice data from the file
    with open(text_file_path, 'r') as file:
        text_data = file.read()

    user_inputs = config_data['components'][1]['userInputs']
    component_name = config_data['components'][1]['name']
    #print("*******config_data**************")
    #print(config_data)
    # model_path = get_model_path(component_name)
    # tokenizer, model = load_model_and_tokenizer(model_path)

    # Create the structured prompt (JSON) from the LLM output
    # structured_prompt = create_prompt(config_data, model_path, user_inputs['systemMessage'], user_inputs['input'], text_data)

    # Optionally, perform further processing or modifications on structured_prompt if needed
    # e.g., structured_prompt["headers"]["invoice_number"] = "new_invoice_number"
    #projectName = config_data['projectName']
    # Pass the structured prompt to the generative AI model for further processing
    # output = generative_ai_dynamic_prompting(projectName, structured_prompt, text_file_path, tokenizer, model)
    structured_prompt = config_data['dynamic_prompt_data']

    #print("structured_prompt",structured_prompt)
    output = generative_ai_dynamic_prompting(structured_prompt, text_file_path)

    print("This is the final response:", output)

    # Save the generated JSON output to the specified output file
    with open(output_file_path, 'w') as out_file:
        json.dump(output, out_file, indent=4)

    return output








# meta prompt code starts froms here
def generative_ai_meta_prompt(user_prompt, model_name):
    try:
        
        # if model_name == "gemini":
        #     model = "vertex_ai.gemini-1.5-pro'
        # elif model_name == "openai":
        #     model = "azure.gpt-4o-2024-11-20"
        # elif model_name == "anthropic":
        #     model = "bedrock.anthropic.claude-3-5-sonnet-v2"
        # model_path = get_model_path(model_name)
        # tokenizer, model = load_model_and_tokenizer(model_path)
        print("---user_prompt_content---")
        ##print(type(user_prompt_json_content))
        print(user_prompt)

        # user_prompt_json_content = json.loads(user_prompt)
        # user_prompt_headers = user_prompt_json_content["header"]
        # user_prompt_lineitems = user_prompt_json_content["table"]
        # #print(type(user_prompt_headers))
        # #print("user_prompt_headers", user_prompt_headers)
        
        # #print("header and table data extracted from json")

        
        meta_prompt = construct_llm_meta_prompt(user_prompt)
        
        header_line_item = genai_main(meta_prompt)
        print("**************header_line_item***************")
        print(header_line_item)
        clean_header_line_item = clean_response(header_line_item)
        #print("**************clean_header_line_item***************")
        print(clean_header_line_item)
        
        
        custom_dict = list(clean_header_line_item['headers'].keys())
        prompt_custom_dict = list(clean_header_line_item['headers'].values())
        
        # Table custom dictionary and prompt extraction
        table_custom_dict = [f"{key}|{key}" for key in clean_header_line_item['line_items'].keys()]
        prompt_table_custom_dict = list(clean_header_line_item['line_items'].values())
        
        # Output result in the desired format
        result = {
            'custom_dict': custom_dict,
            'prompt_custom_dict': prompt_custom_dict,
            'table_custom_dict': table_custom_dict,
            'prompt_table_custom_dict': prompt_table_custom_dict
        }
        
        # Convert result to JSON formatted string for output purposes
        output_json = json.dumps(result, indent=2)
      
        #print("**************Gen ai model response***************")
        #print(output_json)

        return output_json
    except Exception as e:
            #print("Error in generative_ai_dynamic_prompting",e)
            return ""



def generative_ai_meta_prompt_config(user_prompt,model_name):
    try:
        if model_name == "gemini":
            model = "vertex_ai.gemini-1.5-pro"
        elif model_name == "openai":
            model = "azure.gpt-4o-2024-11-20"
        elif model_name == "claude":
            model = "bedrock.anthropic.claude-3-5-sonnet-v2"
    
        print("---user_prompt_content---")
        print(type(user_prompt_json_content))
        print(user_prompt)
    
        
        meta_prompt = construct_llm_meta_prompt_config(user_prompt)
        
        header_line_item = genai_main(meta_prompt, model)
        print("**************header_line_item***************")
        print(header_line_item)
        clean_header_line_item = clean_response(header_line_item)
        #print("**************clean_header_line_item***************")
        print(clean_header_line_item)
        
        
        custom_dict = list(clean_header_line_item['headers'].keys())
        prompt_custom_dict = list(clean_header_line_item['headers'].values())
        
        # Table custom dictionary and prompt extraction
        table_custom_dict = [f"{key}|{key}" for key in clean_header_line_item['line_items'].keys()]
        prompt_table_custom_dict = list(clean_header_line_item['line_items'].values())
        
        # Output result in the desired format
        result = {
            'custom_dict': custom_dict,
            'prompt_custom_dict': prompt_custom_dict,
            'table_custom_dict': table_custom_dict,
            'prompt_table_custom_dict': prompt_table_custom_dict
        }
        
        # Convert result to JSON formatted string for output purposes
        output_json = json.dumps(result, indent=2)
      
        #print("**************Gen ai model response***************")
        #print(output_json)
    
        return output_json
    except Exception as e:
            #print("Error in generative_ai_dynamic_prompting",e)
            return ""




def clean_response(data):
    try:
        json_data=""
        json_match = re.search(r'\{.*\}', data, re.DOTALL)
        try:
            if json_match:
                json_data = json_match.group(0)
            data = json.loads(json_data)
            pretty_json = json.dumps(data, indent=4)
        except json.JSONDecodeError as e:
            #print("Invalid JSON:", e)
            return ""
        return data
    except Exception as e:
            #print("Error in clean_response:", e)
            return ""


def construct_llm_meta_prompt(user_prompt):
    """
    Use the LLM to generate a meta prompt that describes what the user wants to extract from the text.
    The LLM will help determine how to phrase the prompt based on the user's description.
    """
    try:
        filename = '/data/digital_workmate_agentic/extraction_app/app/genai/meta_prompt/prompt_template_meta_prompt.txt'
        #digital_workmate_agentic/extraction_app/app/genai/meta_prompt/prompt_template_meta_prompt.txt
        with open(filename, 'r') as file:
            meta_prompt_generation_prompt = file.read()
             # Create a prompt to ask the LLM to generate a meta prompt


        response_format = """
                        {
                          "headers": {
                            "<field_name>": "prompt text here",
                            "<field_name>": "prompt text here"
                          },
                          "line_items": {
                            "<field_name>": "prompt text here",
                            "<field_name>": "prompt text here"
                          }
                        }
                        
        """

        if isinstance(user_prompt, tuple):
                user_prompt = " ".join(map(str, user_prompt))  # Convert tuple to string
        elif not isinstance(user_prompt, str):
            raise ValueError("Data must be a string or tuple of strings")
        
        # Convert json_data dictionary to a JSON string
        #json_data_str = json.dumps(user_prompt)
        # Replace placeholders in the prompt with actual data
        meta_prompt_generation_prompt = meta_prompt_generation_prompt.replace("{user_prompt}", user_prompt).replace("{response_format}", response_format)
    
        #print("-----meta_prompt_generation_prompt-----")
        #print(meta_prompt_generation_prompt)
        # Extract the generated meta prompt from the response
        #meta_prompt =  generate_text(meta_prompt_generation_prompt, max_new_tokens= 2000)
        
        return meta_prompt_generation_prompt

    except Exception as e:
        #print("Error in construct_meta_prompt:", e)
        return ""

def construct_llm_meta_prompt_config(user_prompt):
    """
    Use the LLM to generate a meta prompt that describes what the user wants to extract from the text.
    The LLM will help determine how to phrase the prompt based on the user's description.
    """
    try:
        filename = '/data/digital_workmate_agentic/extraction_app/app/genai/meta_prompt/prompt_template_meta_prompt_config.txt'
        #digital_workmate_agentic/extraction_app/app/genai/meta_prompt/prompt_template_meta_prompt.txt
        with open(filename, 'r') as file:
            meta_prompt_generation_prompt = file.read()
             # Create a prompt to ask the LLM to generate a meta prompt


        response_format = """
                        {
                          "headers": {
                            "<field_name>": "prompt text here",
                            "<field_name>": "prompt text here"
                          },
                          "line_items": {
                            "<field_name>": "prompt text here",
                            "<field_name>": "prompt text here"
                          }
                        }
                        
        """

        if isinstance(user_prompt, tuple):
                user_prompt = " ".join(map(str, user_prompt))  # Convert tuple to string
        elif not isinstance(user_prompt, str):
            raise ValueError("Data must be a string or tuple of strings")
        
        # Convert json_data dictionary to a JSON string
        #json_data_str = json.dumps(user_prompt)
        # Replace placeholders in the prompt with actual data
        meta_prompt_generation_prompt = meta_prompt_generation_prompt.replace("{user_prompt}", user_prompt).replace("{response_format}", response_format)
    
        #print("-----meta_prompt_generation_prompt-----")
        #print(meta_prompt_generation_prompt)
        # Extract the generated meta prompt from the response
        #meta_prompt =  generate_text(meta_prompt_generation_prompt, max_new_tokens= 2000)
        
        return meta_prompt_generation_prompt

    except Exception as e:
        #print("Error in construct_meta_prompt:", e)
        return ""

def construct_llm_meta_prompt_config_eg(user_prompt):
    """
    Use the LLM to generate a meta prompt that describes what the user wants to extract from the text.
    The LLM will help determine how to phrase the prompt based on the user's description.
    """
    try:
        filename = '/data/digital_workmate_agentic/extraction_app/app/genai/meta_prompt/prompt_template_meta_prompt_config_eg.txt'
        #digital_workmate_agentic/extraction_app/app/genai/meta_prompt/prompt_template_meta_prompt.txt
        with open(filename, 'r') as file:
            meta_prompt_generation_prompt = file.read()
             # Create a prompt to ask the LLM to generate a meta prompt


        response_format = """
                        {
                          "headers": {
                            "<field_name>": "prompt text here",
                            "<field_name>": "prompt text here"
                          },
                          "line_items": {
                            "<field_name>": "prompt text here",
                            "<field_name>": "prompt text here"
                          }
                        }
                        
        """

        if isinstance(user_prompt, tuple):
                user_prompt = " ".join(map(str, user_prompt))  # Convert tuple to string
        elif not isinstance(user_prompt, str):
            raise ValueError("Data must be a string or tuple of strings")
        
        # Convert json_data dictionary to a JSON string
        #json_data_str = json.dumps(user_prompt)
        # Replace placeholders in the prompt with actual data
        meta_prompt_generation_prompt = meta_prompt_generation_prompt.replace("{user_prompt}", user_prompt).replace("{response_format}", response_format)
    
        #print("-----meta_prompt_generation_prompt-----")
        #print(meta_prompt_generation_prompt)
        # Extract the generated meta prompt from the response
        #meta_prompt =  generate_text(meta_prompt_generation_prompt, max_new_tokens= 2000)
        
        return meta_prompt_generation_prompt

    except Exception as e:
        #print("Error in construct_meta_prompt:", e)
        return ""


# def generate_llm_text(tokenizer,model,content, max_new_tokens, temp=0.1):
#     try:
#         # #print("-------------content start---------------")
#         # #print(content)
#         # #print("-------------content end---------------")
#         inputs = tokenizer(content, return_tensors="pt").to('cuda')
#         outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, output_scores=False, return_dict_in_generate=True, do_sample=False,temperature=temp)
#         generated_tokens = outputs.sequences[0][len(inputs.input_ids[0]):]
    
#         # Decode generated text
#         generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
#         del inputs
#         del outputs
#         del generated_tokens
#         torch.cuda.empty_cache()
#         # #print("clearning cache")
#         # command = "sync; echo 1 > /proc/sys/vm/drop_caches"

#         # # Use subprocess.run to execute the command
#         # # The 'sudo' part needs to be run in the shell
#         # subprocess.run(f"sudo {command}", shell=True, check=True)
#         # #print("cache cleared")
#         return generated_text
#     except Exception as e:
#             #print("Error in generate_llm_text:", e)
#             return ""




def genai_main(prompt_text, model):
    payload = {
        #"model": "vertex_ai.gemini-1.5-pro",
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a smart assistant designed to help extract key fields from invoices. Your task is to create a meta-prompt that defines how to identify and extract relevant fields."
            },
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        "max_tokens": 5000
    }

    # Send request to Azure OpenAI endpoint
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.post(
       f"{base_url}/openai/deployments/vertex_ai.gemini-1.5-pro/chat/completions",
        headers=headers,
        json=payload
    )
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"