from flask import Flask, request
import os
import re
import ast
import torch
import torch.nn.functional as F
import json
import pandas as pd
from collections import OrderedDict
import subprocess
import requests
# from ..web_app.backend_web.invoiceapp.api_views import add_fields_configuration_dynamic

from .db_codes.add_config_dict_mapping import map_fields

        
def generative_ai_dynamic_prompting(projectName, dynamic_data, txt_file_path, tokenizer, model):
    try:
        user_prompt_headers_string= ""
        # Opening the invoice file in read mode
        with open(txt_file_path, 'r') as file:
            # Read the entire content of the file
            invoice_text = file.read()
        
        #print("dynamic_data---", dynamic_data)
        header_prompt = dynamic_data['headers']
        line_items_prompt = dynamic_data['line_items']
        #print("header_prompt")
        #print(header_prompt)
        #print("line_items_prompt")
        #print(line_items_prompt)

        # need to check if headers or line items are empty
    
        final_input_header, header_keys_project_config = prompting_headers(header_prompt, invoice_text)
        #print(header_keys_project_config,"@@@@@@@###")
        #print("final_input_header")
        #print(final_input_header)
        #print("creating header response by llm call")
        extracted_header = generate_text(tokenizer,model,final_input_header, max_new_tokens= 1000)
        #print("**************extracted_header***************")
        #print(extracted_header)
        clean_extracted_header = clean_response(extracted_header)

        
        final_input_header_confidence = prompting_headers_confidence(header_prompt, invoice_text, clean_extracted_header)
        #print("creating header confidence response by llm call")
        extracted_header_confidence = generate_text(tokenizer,model,final_input_header_confidence, max_new_tokens= 500)
        #print("**************extracted_header_confidence***************")
        #print(extracted_header_confidence)
        clean_extracted_header_confidence = clean_response(extracted_header_confidence)
        #print("**************clean_extracted_header_confidence***************")
        #print(clean_extracted_header_confidence)
        
        # extracted_merged_headers = {"headers": {key: [value, 100 if value else 0] for key, value in clean_extracted_header["headers"].items()}} 
        # #print("**************extracted_merged_headers***************")
        # #print(extracted_merged_headers)

        #print("***creating confidence score******")
        extracted_merged_headers = {"headers": {}}   
        for key in clean_extracted_header["headers"]:  
            confidence_key = key + "_confidence_score"  
            extracted_merged_headers["headers"][key] = [
                clean_extracted_header["headers"][key], 
                int(clean_extracted_header_confidence["headers_confidence_score"].get(confidence_key, ""))
            ]
        #print("_________________-merged_headers_________________")
        #print(extracted_merged_headers)

        if line_items_prompt:
            
            final_input_lineitems, line_keys_project_config = prompting_line_item(line_items_prompt, invoice_text)
           
            #print("creating line item response by llm call")
            extracted_lineitems = generate_text(tokenizer,model,final_input_lineitems, max_new_tokens= 1000)
            #print("**************extracted_lineitems***************")
            #print(extracted_lineitems)
            clean_extracted_line = clean_response(extracted_lineitems)
            #print("**************clean_extracted_lineitems***************")
            #print(clean_extracted_line)


        if line_items_prompt:
            #print("There is line items")
            output = {  
                "static": extracted_merged_headers["headers"],  
                "dynamic": []  
            }  
            #print("output",output)
            #print(type(clean_extracted_line))
            
            # Extract keys for line items  
            keys = list(clean_extracted_line["line_items"][0].keys())
            #print('keys')
            #print(keys)
            output["dynamic"].append(keys)  
            #print("output",output)
            # Extract values for each line item  
            values_list = []  
            for item in clean_extracted_line["line_items"]:  
                values = [item[key] for key in keys]  
                values_list.append(values)  
              
            output["dynamic"].append(values_list)  
            
        else:
            #print("There is NO line items")
            output = {  
                "static": extracted_merged_headers["headers"],  
                "dynamic": [[]]
            }  
        #print("--------sending data to web app for config list--------")
        # response_add_config = add_fields_configuration_dynamic(config_data, user_id, company_code)
        # #print(response_add_config,"===============")
        ##make api here which will send my data of config_data ###
        #print("**************Gen ai model response***************")
        #print(output)
        

        return output
    except Exception as e:
            #print("Error in generative_ai_dynamic_prompting",e)
            return ""



def prompting_headers(header_prompt, invoice_text):
    try:
        filename = '/data/digitalworkmate/product_dev/extraction_app/app/nlp/domestic/gen_ai/dynamic_prompt_template_headers.txt'
        with open(filename, 'r') as file:
            prompt_template_headers = file.read()

        # Create new dictionaries with empty strings as values for headers
        header_with_empty_values = {key: "" for key in header_prompt.keys()}
        header_with_empty_values_db =  {key: "" for key in header_prompt.keys()}
        header_with_empty_values = {"headers": header_with_empty_values}
        # if isinstance(header_with_empty_values, tuple):
        #     header_with_empty_values = " ".join(map(str, header_with_empty_values))  # Convert tuple to string
        # elif not isinstance(header_with_empty_values, str):
        #     traceback.#print_exe()
        #     raise ValueError("Data must be a string or tuple of strings")
            
                
        # if isinstance(header_prompt, tuple):
        #     header_prompt = " ".join(map(str, header_prompt))  # Convert tuple to string
        # elif not isinstance(header_prompt, str):
        #     raise ValueError("header_json must be a string or tuple of strings")
        
        formatted_header = '\n'.join([f'"{key}": "{value}"' for key, value in header_prompt.items()])

        # Convert json_data dictionary to a JSON string
        header_with_empty_values = json.dumps(header_with_empty_values)

        #header_prompt = json.dumps(header_prompt)
        #print("header_prompt inside prompting headers")
        #print(header_prompt)
        # Replace placeholders in the prompt with actual data
        prompt_template_headers = prompt_template_headers.replace("{json_data}", header_with_empty_values).replace("{header_prompt}", formatted_header).replace("{invoice_text}", invoice_text)
        
        return prompt_template_headers, header_with_empty_values_db
    except Exception as e:
            #print("Error in prompting_headers",e)
            return ""

def prompting_line_item(lineitem_prompt, invoice_text):
    try:
        filename = '/data/digitalworkmate/product_dev/extraction_app/app/nlp/domestic/gen_ai/dynamic_prompt_template_line_items.txt'
        with open(filename, 'r') as file:
            prompt_template_lineitem = file.read()
        
        # Create the structure for line items by dynamically using keys from the data
        line_items_values = [{key: "" for key in lineitem_prompt.keys()}]
        line_items_values_db = {key: "" for key in lineitem_prompt.keys()}
        #print("line_items_values1",line_items_values)
        # Format the output with a trailing comma
        line_items_with_empty_values = '[' + ', '.join([str(item) for item in line_items_values]) + ',]'

        line_items_with_empty_values = {"line_items": line_items_with_empty_values}
        #print("line_items_with_empty_values2  ",line_items_with_empty_values)
        #print(type(line_items_with_empty_values))
        # Convert json_data dictionary to a JSON string
        line_items_with_empty_values = json.dumps(line_items_with_empty_values)
        #print(type(line_items_with_empty_values))
        line_items_with_empty_values = json.loads(line_items_with_empty_values)
        #print(type(line_items_with_empty_values))
                # Convert the string to an actual Python list
        line_items_with_empty_values = ast.literal_eval(line_items_with_empty_values['line_items'])
        
        # Construct the new dictionary with the corrected list
        line_items_with_empty_values = {
            "line_items": line_items_with_empty_values
        }
        
        line_items_with_empty_values = json.dumps(line_items_with_empty_values)
        #print("line_items_with_empty_values 3 ",line_items_with_empty_values)
        
        #print(type(line_items_with_empty_values))
        
        formatted_lineitem = '\n'.join([f'"{key}": "{value}"' for key, value in lineitem_prompt.items()])
        # Replace placeholders in the prompt with actual data
        prompt_template_lineitem = prompt_template_lineitem.replace("{json_data}", line_items_with_empty_values).replace("{line_prompt}", formatted_lineitem).replace("{invoice_text}", invoice_text)
        #print(line_items_values_db,"--------------------------------------------------------------")
        return prompt_template_lineitem, line_items_values_db
    except Exception as e:
            #print("Error in prompting_line_item",e)
            return ""


def prompting_headers_confidence(header_prompt, invoice_text,clean_extracted_header):
    try:
        filename = '/data/digitalworkmate/product_dev/extraction_app/app/nlp/domestic/gen_ai/dynamic_prompt_template_header_confidence.txt'
        with open(filename, 'r') as file:
            prompt_template_confidence = file.read()

        # Create new dictionaries with empty strings as values for headers
        header_with_empty_values = {key: "" for key in header_prompt.keys()}
        #print("header_with_empty_values")
        #print(header_with_empty_values)
        # Add "_confidence_score" to each key
        Key = {key + "_confidence_score": '' for key in header_with_empty_values}
        
        json_headers = {
            'headers_confidence_score': Key
        }
        json_headers = json.dumps(json_headers, indent=4)
        #print("json_headers")
        #print(json_headers)

        confidence_texts = []
        for key in header_with_empty_values:
            # Construct the new key with "_confidence_score" suffix
            new_key = f"{key}_confidence_score"
            
            # Construct the confidence score message
            confidence_text = f"{new_key}: Give the Confidence Score between 0 and 100 of {key},"
            
            # Add the confidence text to the list
            confidence_texts.append(confidence_text)
        
        # Join all confidence texts with newline for clarity
        final_text = "\n".join(confidence_texts)
        
        # #print and return the final confidence text
        #print("final_text")
        #print(final_text)
        
       
        # Convert json_data dictionary to a JSON string
        header_with_empty_values = json.dumps(header_with_empty_values)
        clean_extracted_header = json.dumps(clean_extracted_header)
        #print(type(json_headers))
        #print(type(final_text))
        #print(type(invoice_text))
        #print(type(clean_extracted_header))
        # Replace placeholders in the prompt with actual data
        prompt_template_confidence = prompt_template_confidence.replace("{json_data}", json_headers).replace("{header_prompt_confidence}", final_text).replace("{invoice_text}", invoice_text).replace("{header_json}", clean_extracted_header)
        
        return prompt_template_confidence
    except Exception as e:
            #print("Error in prompt_template_confidence",e)
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
    

def generate_text(tokenizer,model,content, max_new_tokens, temp=0.1):
    try:
        #print("-------------content start---------------")
        #print(content)
        #print("-------------content end---------------")
        inputs = tokenizer(content, return_tensors="pt").to('cuda')
        outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, output_scores=False, return_dict_in_generate=True, do_sample=False,temperature=temp)
        generated_tokens = outputs.sequences[0][len(inputs.input_ids[0]):]
    
        # Decode generated text
        generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        del inputs
        del outputs
        del generated_tokens
        torch.cuda.empty_cache()
        # #print("clearning cache")
        # command = "sync; echo 1 > /proc/sys/vm/drop_caches"

        # # Use subprocess.run to execute the command
        # # The 'sudo' part needs to be run in the shell
        # subprocess.run(f"sudo {command}", shell=True, check=True)
        # #print("cache cleared")
        return generated_text
    except Exception as e:
            #print("Error in generate_text:", e)
            return ""