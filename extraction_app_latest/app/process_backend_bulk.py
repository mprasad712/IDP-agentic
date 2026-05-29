from ocr.ocr_page import call_ocr
import threading
import requests
import uuid
from collections import OrderedDict
from genai.call_llm import generate_response, generative_ai_meta_prompt, generative_ai_meta_prompt_config, generative_ai_meta_prompt_eg
from genai.gemini import generate_invoice_response
# from digital_workmate_agentic.web_app.backend_web.invoiceapp.business_logic.invoice_upload import invoice_upload
from flask import Flask, jsonify, request
from flask_cors import CORS
from config.db_connection import mapdb_key, insert_file, updated_by_UUID, get_agentic_data, get_fields_prompt_agentic, update_success_processed_status, update_failed_processed_status, update_running_status
import os
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil
import signal
from config import idpSettings
import shutil
global esett
import pandas as pd
import calendar;
import time;
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Font

esett = idpSettings()

app = Flask(__name__)
CORS(app)

ocr_output_base = r"/data/digital_workmate_agentic/extraction_app/ocr_output"
final_output_base = r"/data/digital_workmate_agentic/extraction_app/output/text"

def extract_model_name(json_data):
    models=[]
    for node in json_data['nodes']:
        if node['data']['componentType'] == "Models":
            print(node['data']['name'])
            models.append(node['data']['name'])
    return models

def get_output_filepath_datatype(input_json):
    for node in input_json['nodes']:
        if node['data']['componentType'] == "output_data_source":
            datatype = node['data']['fileType']         
    return datatype
    
def fetch_data_from_api():
    # Example: replace with your actual API call to fetch data
    try:
        response = requests.get("http://10.89.148.84:5002/get_agent_process_live_status/")  # Update with actual endpoint
        if response.status_code == 200:
            print(response.json(),"@@####")
            return response.json()
        else:
            print(f"Error fetching data: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Exception during API call: {e}")
        return None
        
def fetch_dynamic_prompts(agent_name, company_code):
    header, table = get_fields_prompt_agentic(agent_name, company_code)
    if header or table:
        header = {d['field_key']: d['mapped_prompt'] for d in header} if header else {}
        table = {d['field_key']: d['mapped_prompt'] for d in table} if table else {}
        dynamic_prompt_data = {"header": header, "line_items": table}
    else:
        dynamic_prompt_data = {}
    response_data = {"dynamic_prompt_data": dynamic_prompt_data}
    return response_data

def replace_none_with_empty_string(data):
    if isinstance(data, dict):
        return {k: replace_none_with_empty_string(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_none_with_empty_string(item) for item in data]
    else:
        return '' if data is None else data
    
def process_file(file_path, input_json, user_id, company_code):
    # Existing processing logic
    if not os.path.exists(file_path):
        print(f"File {file_path} no longer exists. Skipping processing.")
        return
    print(f"Processing file: {file_path}")
    agent_name = input_json["projectName"]
    file_name = os.path.basename(file_path)
    extractor = FieldExtractor(file_name, user_id, agent_name)
    pdf_file = os.path.basename(file_path)
    ocr_obj = call_ocr(extractor.input_path, extractor.output_path)
    txt_file_path, page_status = ocr_obj.ocr_main()
    output_file_path = os.path.join(final_output_base, os.path.splitext(pdf_file)[0] + '.txt')
    model_names = extract_model_name(input_json)
    model_names = [item for item in model_names if item is not None]
    if model_names[0]:
        model_name = model_names[0]
    else:
        result = {"status": "0", "message": "No Model is selected"}
        return result

    if model_name in ["llama", "phi-4", "Gemini","Claude","OpenAI"]:
        dynamic_prompt_json = fetch_dynamic_prompts(agent_name, company_code)
        result = generate_response( dynamic_prompt_json, txt_file_path, output_file_path)
    else:
        result = "Unsupported model type."

    if result == "":
        result = "Blank output from model."

    config_uuid = input_json["projectName"]
    print("Final response ****************")
    result = replace_none_with_empty_string(result)
    result['static']['file_name'] = [pdf_file, ""]
    print(result)
    
    try:
        datatype = get_output_filepath_datatype(input_json)

        if datatype == 'json':
            # if filepath:
            #     output_dir = filepath
            #     if not os.path.exists(output_dir):
            #         os.makedirs(output_dir)
            # else:
            output_dir = f'/data/digital_workmate_agentic/extraction_app_latest/output/json/{user_id}/{config_uuid}'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            create_json_output(result, output_dir)
        elif datatype == 'excel':
            # if filepath:
            #     output_dir = filepath
            #     if not os.path.exists(output_dir):
            #         os.makedirs(output_dir)
            # else:
            output_dir = f'/data/digital_workmate_agentic/extraction_app_latest/output/excel/{user_id}/{config_uuid}'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            create_excel_from_json(result, output_dir)
        else:
            # if filepath:
            #     output_dir = filepath
            #     if not os.path.exists(output_dir):
            #         os.makedirs(output_dir)
            # else:
            output_dir = f'/data/digital_workmate_agentic/extraction_app_latest/output/excel/{user_id}/{config_uuid}'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            create_excel_from_json(result, output_dir)
    except Exception as e:
        print(e,"_______")
        
    try:
        mapdb_key(result, config_uuid, company_code, user_id, "", "", "")
        update_success_processed_status(agent_name, file_name, company_code, user_id)
        shutil.move(file_path, os.path.join(esett.ROOT_INPUT_DIR, company_code, config_uuid, pdf_file))
        print("Inserted into DB")
    except Exception as e:
        update_failed_processed_status(agent_name, file_name, company_code, user_id)
        print("Not inserted into DB")
        print(e)
    
def continuous_process():
    while True:
        # Step 1: Fetch data from the API
        data = fetch_data_from_api()
        if not data:
            print("No data fetched. Waiting...")
        else:
            for item in data:
                agent_name = item['agent_name']
                user_id = item['user_id']
                company_code = item['company_code']
                file_name = item['file_name']
                update_running_status(agent_name, file_name, company_code, user_id)
                file_loc = f"/data/digital_workmate_agentic/input_queue/{user_id}/{agent_name}"
                file_path = os.path.join(file_loc, file_name)
                
                ##get agentic data from db_connection not web_app api##
                agent_data = get_agentic_data(user_id, company_code, agent_name)
                if agent_data:
                    json_string = agent_data[0]['agent_data']
                    agentic_data = json.loads(json_string)
                try:
                    process_file(file_path,agentic_data, user_id, company_code)
                    update_success_processed_status(agent_name, file_name, company_code, user_id)
                except Exception as e:
                    print(f"Error processing file {file_name}: {e}")
                    update_failed_processed_status(agent_name, file_name, company_code, user_id)

        # Step 2: Wait and fetch again after 5 seconds
        time.sleep(5)


@app.route('/meta_prompt', methods=['POST'])  
def meta_prompt():    
    #print(request.form, "###$$$")
    start_time = time.time()
    global input_json
    input_data = request.json
    print(input_data,"pppppppppppppppppppppppp")
    ##Gloobal##
    global bulk_folder_input_queue_path
    bulk_folder_input_queue_path = os.path.join('/data','digital_workmate_agentic','input_queue',input_data.get("user_id"),input_data.get("agent_name"))
    print(bulk_folder_input_queue_path)
    if not os.path.exists(bulk_folder_input_queue_path):
        os.makedirs(bulk_folder_input_queue_path)
    ##ends##
    user_input = input_data.get("user_prompt")
    model_name = input_data.get("model_name")
    project_type = input_data.get("project_type")
    print("user_input")
    print(user_input)
    print("model_name")
    print(model_name)
    print("project_type")
    print(project_type)
    
    
    # prompt_data = json.loads(user_input)
    
    print("###############---  Creating meta Prompt  ---#############")
    if project_type == 'eg':
        
        # Case 1: Parsing static and dynamic keys
        if 'static' in user_input and 'dynamic' in user_input:
            print("user input is with config")
            json_meta_gen_ai = generative_ai_meta_prompt_config_eg(user_input, model_name)
        else:
            print("egggggg--------------")
            print("user input is without config")
            json_meta_gen_ai = generative_ai_meta_prompt_eg(user_input, model_name)
    else:
        # Case 1: Parsing static and dynamic keys
        if 'static' in user_input and 'dynamic' in user_input:
            print("user input is with config")
            json_meta_gen_ai = generative_ai_meta_prompt_config(user_input, model_name)
        else:
            print("user input is without config")
            json_meta_gen_ai = generative_ai_meta_prompt(user_input, model_name)
    
    print("************json_meta_gen_ai**********")
    print(type(json_meta_gen_ai))
    print(json_meta_gen_ai)

    return json_meta_gen_ai


# Create excel report for final result
def create_excel_from_json(data, output_dir):
    try:

        # Extracting data from JSON
        os.makedirs(output_dir, exist_ok=True)
        print(output_dir,"##$")
        static_data = data.get('static', {})
        dynamic_data_list = data.get('dynamic', [])
        
        # Get the full file name including extension
        file_name_full = static_data.get('file_name', ['output.xlsx'])[0]
        
        # Prepare the file name without extension for the Excel file name
        file_name_without_ext = file_name_full.replace('.pdf', '')

        # Select only the first value from each list in 'static' and ensure 'file_name' comes first
        static_data_ordered = {'file_name': [file_name_full]}
       
        for k, v in static_data.items():
            if k != 'file_name':
                static_data_ordered[k] = [v[0]] if isinstance(v, list) else [v]
        static_df = pd.DataFrame(static_data_ordered)

        try:
            # Prepare dynamic data into a DataFrame
            if len(dynamic_data_list) > 1:
                dynamic_columns = dynamic_data_list[0]  # First sublist contains the column headers
                dynamic_data = dynamic_data_list[1]  # Second sublist contains the rows of data
                dynamic_df = pd.DataFrame(dynamic_data, columns=dynamic_columns)
            else:
                dynamic_df = pd.DataFrame()
        except Exception as e:
            dynamic_df = pd.DataFrame()
            print(e,"###")

        # Define the path for the Excel file, using the filename without the extension
        excel_file_path = os.path.join(output_dir, f"{file_name_without_ext}.xlsx")

        # Create an Excel writer with openpyxl
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            # Write 'headers' from the dataframe and apply styles
            static_df.to_excel(writer, index=False, sheet_name='headers')
            workbook = writer.book
            sheet1 = workbook['headers']
            for cell in sheet1[1]:
                cell.font = Font(bold=True)

            # Write 'line_items' from the dataframe and apply styles
            dynamic_df.to_excel(writer, index=False, sheet_name='line_items')
            sheet2 = workbook['line_items']
            for cell in sheet2[1]:
                cell.font = Font(bold=True)

        print(f"Excel file '{excel_file_path}' created successfully with sheets 'headers' and 'line_items'.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Create excel report for final result
def create_json_output(data, output_dir):
    try:
        
        # Extracting data from JSON
        os.makedirs(output_dir, exist_ok=True)
        file_name_full = data['static']['file_name'][0]
        file_name_without_ext = file_name_full.replace('.pdf', '')
        json_file_path = os.path.join(output_dir, f"{file_name_without_ext}.json")
        # Write the data to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        print(f"JSON file '{json_file_path}' created successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# ************************** End of the Code *****************************************
class FieldExtractor():
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = "2"
    def __init__(self, file, user_id, agent_name=None):
        self.file = file
        self.user_id = user_id
        self.agent_name = agent_name
   
    @property
    def input_path(self):
        if os.path.exists(self.file):
            return self.file
        else:
            return  os.path.join(esett.ROOT_INPUT_DIR_INPUT_QUEUE, self.user_id, self.agent_name, self.file)
    @property
    def output_path(self):
        output_dir = os.path.join(esett.OUTPUT_DIR, self.user_id)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        print(output_dir,"*****************************")
        output_dir = os.path.join(esett.OUTPUT_DIR, self.user_id,self.agent_name)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        return output_dir

        

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'invalid input'}), 404)

if __name__ == '__main__':
    # Start the continuous processing thread when the application starts
    processing_thread = threading.Thread(target=continuous_process, daemon=True)
    processing_thread.start()

    # Start the Flask app
    app.run(host='0.0.0.0', port=5004, debug=False)