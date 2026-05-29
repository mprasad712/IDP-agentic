from ocr.ocr_page import call_ocr
import uuid
from genai.call_llm import generate_response, generative_ai_meta_prompt, generative_ai_meta_prompt_config, generative_ai_meta_prompt_eg
from genai.gemini import generate_invoice_response
# from digital_workmate_agentic.web_app.backend_web.invoiceapp.business_logic.invoice_upload import invoice_upload
from flask import Flask, jsonify, request
from flask_cors import CORS
from config.db_connection import mapdb_key, insert_file, updated_by_UUID
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
from threading import Lock

esett = idpSettings()

app = Flask(__name__)
CORS(app)

ocr_output_base = r"/data/digital_workmate_agentic/extraction_app/ocr_output"
final_output_base = r"/data/digital_workmate_agentic/extraction_app/output/text"
final_pdf = r"/data/digital_workmate_agentic/web_app/backend_web/invoiceapp/static/eips_data/invoice_data"

active_observers = {}

class FileHandler(FileSystemEventHandler):
    def __init__(self, input_json, target_directory, UUID, user_id, company_code):
        self.input_json = input_json
        self.target_directory = target_directory
        self.UUID = UUID
        self.user_id = user_id
        self.company_code = company_code

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            process_file(event.src_path, self.input_json, self.UUID, self.user_id, self.company_code)
 



def process_file(file_path, input_json, UUID, user_id, company_code):
    # Check if the file exists before processing
    if not os.path.exists(file_path):
        print(f"File {file_path} no longer exists. Skipping processing.")
        return
    pdf_file = os.path.basename(file_path)
    ocr_obj = call_ocr(file_path, ocr_output_base)
    txt_file_path, page_status = ocr_obj.ocr_main()
    output_file_path = os.path.join(final_output_base, os.path.splitext(pdf_file)[0] + '.txt')
    model_name = get_model_name(input_json)
    
    if model_name[0] in ["llama", "phi-4", "Gemini","Claude"]:
        result = generate_response(input_json, txt_file_path, output_file_path)
    else:
        result = "Unsupported model type."

    if result == "":
        result = "Blank output from model."

    config_uuid = input_json["projectName"]
    company_code = str(input_json["company_code"])
    user_id = str(input_json["user_id"])
    print("Final response ****************")
    result = replace_none_with_empty_string(result)
    result['static']['file_name'] = [pdf_file, ""]
    print(result)
    
    try:
        filepath, datatype = get_output_filepath_datatype(input_json)

        if datatype == 'json':
            if filepath:
                output_dir = filepath
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            else:
                output_dir = f'/data/digital_workmate_agentic/extraction_app/output/json/{user_id}/{config_uuid}'
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            create_json_output(result, output_dir)
        elif datatype == 'excel':
            if filepath:
                output_dir = filepath
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            else:
                output_dir = f'/data/digital_workmate_agentic/extraction_app/output/excel/{user_id}/{config_uuid}'
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            create_excel_from_json(result, output_dir)
        else:
            if filepath:
                output_dir = filepath
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            else:
                output_dir = f'/data/digital_workmate_agentic/extraction_app/output/excel/{user_id}/{config_uuid}'
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            create_excel_from_json(result, output_dir)
    except Exception as e:
        print(e,"_______")
        
   
    
    try:
        mapdb_key(result, config_uuid, company_code, user_id, "", "", "")
        print("Inserted into DB")
    except Exception as e:
        print(e)
    
    shutil.move(file_path, os.path.join(esett.ROOT_INPUT_DIR, company_code, config_uuid, pdf_file))


def get_output_filepath_datatype(input_json):
    # Iterate over the components
    for component in input_json['components']:
        # Check if the component name is 'upload_file'
        if component['name'] == 'output':
            # If so, extract the file name
            file_name = component['userInputs'].get('fileName')
            datatype = component['userInputs'].get('dataType')
            # Continue your code logic here
            
    return file_name, datatype


##new_ui
def get_model_name(json_data):
    models=[]
    for node in json_data['agentData']['nodes']:
        print(node)
        if node['data']['componentType'] == "Models":
            print(node['data']['name'])
            models.append(node['data']['name'])
    return models

def get_pdf_filename(json_data, config_id,user_id):
    for node in json_data['agentData']['nodes']:
        if node['data']['componentType'] == "input_data_source":
            print(node['data']['name'])
            if node['data']['name']:
                pdf = node['data']['name']
                if pdf == 'Directory':
                    if node['data']['path']:
                        file_path =  node['data']['path']
    if pdf == 'Directory':
        file_name = file_path
        print(f"File name for upload_file component: {file_name}")
    elif pdf == 'UploadFile':
        file_name = f'/data/digital_workmate_agentic/input_queue/{user_id}/{config_id}'
    return file_name
##ends

@app.route('/run_agentic_project_bulk', methods=['POST'])
def process_request():
    input_json = request.json
    print(input_json,"@@@")
    config_id = input_json["projectName"]
    user_id = str(input_json["user_id"])
    company_code = str(input_json["company_code"])
    filename = get_pdf_filename(input_json, config_id, user_id)
    UUID = str(uuid.uuid4().hex[:8])
    observer_key = f"{user_id}_{config_id}"
    bulk_folder_input_queue_path = f'/data/digital_workmate_agentic/input_queue/{user_id}/{config_id}'
    output_dir = os.path.join(esett.ROOT_INPUT_DIR, company_code, config_id)
    is_dir = False
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for node in input_json['agentData']['nodes']:
        if node['data']['componentType'] == "input_data_source":
            if node['data']['name'] == 'UploadFile':
                is_dir = True
    
    if filename.endswith('pdf') or filename.endswith('PDF') or is_dir:
        input_path = bulk_folder_input_queue_path
    else:
        input_path = filename
    all_results = []
    if os.path.isdir(input_path):
        # Process existing PDF files
        for file_name in os.listdir(input_path):
            file_path = os.path.join(input_path, file_name)
            if os.path.isfile(file_path) and file_path.lower().endswith('.pdf'):
                now = datetime.now()
                todayDate = now.strftime('%Y-%m-%d %H:%M:%S')
                insert_file(filename, user_id, "1", UUID, config_id, company_code, todayDate)
                try:
                    process_file(file_path, input_json, UUID, user_id, company_code)
                except Exception as e:
                    print(e)
        # If agent is already running for this user, don't restart
        if observer_key in active_observers:
            return jsonify({"status": "failure", "message": "Agent already running for this user and project."})
        # Start new observer
        observer = Observer()
        event_handler = FileHandler(input_json, input_path, UUID, user_id, company_code)
        observer.schedule(event_handler, path=input_path, recursive=False)
        observer.start()
        active_observers[observer_key] = observer
        print("Started monitoring for:", observer_key)
        response_data = {"status": "success", "message": "Monitoring for new files.", "results": all_results}
    else:
        response_data = {"status": "failure", "message": "Input path is not a directory."}
    return jsonify(response_data)


@app.route('/stop_project', methods=['POST'])
def stop_bulk():
    data = request.json
    user_id = str(data.get("user_id"))
    config_id = str(data.get("projectName"))
    observer_key = f"{user_id}_{config_id}"
    observer = active_observers.get(observer_key)
    if observer:
        try:
            observer.stop()
            observer.join()
            del active_observers[observer_key]
            return jsonify({"status": "success", "message": "Agent stopped successfully."})
        except Exception as e:
            return jsonify({"status": "failure", "message": f"Error stopping agent: {str(e)}"})
    else:
        return jsonify({"status": "failure", "message": "No agent running for this user and project."})


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


def replace_none_with_empty_string(data):
    if isinstance(data, dict):
        return {k: replace_none_with_empty_string(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_none_with_empty_string(item) for item in data]
    else:
        return '' if data is None else data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=False)
