from flask import Flask, request
import os
import re
import torch
import torch.nn.functional as F
import json
import pandas as pd
from collections import OrderedDict
import subprocess

def generative_ai_meta_prompt(user_prompt, tokenizer, model):
    try:
        
        
        print("---user_prompt_content---")
        #print(type(user_prompt_json_content))
        print(user_prompt)

        # user_prompt_json_content = json.loads(user_prompt)
        # user_prompt_headers = user_prompt_json_content["header"]
        # user_prompt_lineitems = user_prompt_json_content["table"]
        # print(type(user_prompt_headers))
        # print("user_prompt_headers", user_prompt_headers)
        
        # print("header and table data extracted from json")

        
        meta_prompt = construct_meta_prompt(user_prompt)
        print(meta_prompt,"@@@@@@@@@@@@@@###############_-----------------")
        
        header_line_item = generate_text(tokenizer,model,meta_prompt, max_new_tokens= 2000)
        print("**************header_line_item***************")
        print(header_line_item)
        clean_header_line_item = clean_response(header_line_item)
        print("**************clean_header_line_item***************")
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
        print(result,"@@@@@@@@@@@@@-----------------")
        # Convert result to JSON formatted string for output purposes
        output_json = json.dumps(result, indent=2)
      
        print("**************Gen ai model response***************")
        print(output_json)

        return output_json
    except Exception as e:
            print("Error in generative_ai_dynamic_prompting",e)
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
            print("Invalid JSON:", e)
            return ""
        return data
    except Exception as e:
            print("Error in clean_response:", e)
            return ""


def construct_meta_prompt(user_prompt,system_message,json_data):
    """
    Use the LLM to generate a meta prompt that describes what the user wants to extract from the text.
    The LLM will help determine how to phrase the prompt based on the user's description.
    """
    try:
        filename = '/data/digital_workmate_agentic/extraction_app/app/genai/meta_prompt/meta_prompt.txt'
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
                component_data = json_data['components'][1]['userInputs']
                system_message = component_data['systemMessage']
                user_input = component_data['input']  # Convert tuple to string
        elif not isinstance(user_prompt, str):
            raise ValueError("Data must be a string or tuple of strings")
        
        # Convert json_data dictionary to a JSON string
        #json_data_str = json.dumps(user_prompt)
        # Replace placeholders in the prompt with actual data
        meta_prompt_generation_prompt = meta_prompt_generation_prompt.replace("{user_prompt}", user_prompt).replace("system_message",system_message).replace("{response_format}", response_format)
    
        print("-----meta_prompt_generation_prompt-----")
        print(meta_prompt_generation_prompt,"@@#######$$$$$$$$$$$")
        # Extract the generated meta prompt from the response
        #meta_prompt =  generate_text(meta_prompt_generation_prompt, max_new_tokens= 2000)
        
        return meta_prompt_generation_prompt

    except Exception as e:
        print("Error in construct_meta_prompt:", e)
        return ""


def generate_text(tokenizer,model,content, max_new_tokens, temp=0.1):
    try:
        print("-------------content start---------------")
        print(content)
        print("-------------content end---------------")
        inputs = tokenizer(content, return_tensors="pt").to('cuda')
        outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, output_scores=False, return_dict_in_generate=True, do_sample=False,temperature=temp)
        generated_tokens = outputs.sequences[0][len(inputs.input_ids[0]):]
    
        # Decode generated text
        generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        del inputs
        del outputs
        del generated_tokens
        torch.cuda.empty_cache()
        # print("clearning cache")
        # command = "sync; echo 1 > /proc/sys/vm/drop_caches"

        # # Use subprocess.run to execute the command
        # # The 'sudo' part needs to be run in the shell
        # subprocess.run(f"sudo {command}", shell=True, check=True)
        # print("cache cleared")
        return generated_text
    except Exception as e:
            print("Error in generate_text:", e)
            return ""
