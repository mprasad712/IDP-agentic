from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse
import ast
import requests
from django.conf import settings
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view
import re 
import json
from django.views.decorators.csrf import csrf_exempt 
from django.core.serializers.json import DjangoJSONEncoder
import shutil
from django.http import *
from django.shortcuts import redirect
from django.template import RequestContext 
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import logout as django_logout
from django.views.decorators.cache import cache_control
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import pandas as pd
import csv
import os

from invoiceapp.business_logic.agentic_items import AgenticItems
from invoiceapp.business_logic.customfields import customfields
from .api_views import add_fields_configuration_prompt


def prompt_get(data):
    # Names to look for
    target_names = ["phi-4", "openai", "gemini", "llama"]
    # Iterate over components to find the matching one
    for component in data["components"]:
        if component["name"] in target_names:
            user_input = component["userInputs"].get("input", None)
            if user_input:
                return user_input
            else:
                user_input = ""
                return user_input


# Function to extract the specified name from the ID
def extract_specified_name(component_id):
    pattern = re.compile(r'^(gemini|openai|llama|phi-4)', re.IGNORECASE)
    match = pattern.match(component_id)
    if match:
        return match.group(1)
    return None
    
###new ui
def extract_model_name(json_data):
    models=[]
    for node in json_data['nodes']:
        print(node)
        if node['data']['componentType'] == "Models":
            print(node['data']['name'])
            models.append(node['data']['name'])
    return models

def get_prompts_from_models(nodes):
    prompts = []
    for node in nodes:
        if node['data']['componentType'] == "Models":
            # Use 'get' method to return an empty string if 'prompt' is not found
            prompts.append(node['data'].get('prompt', ""))
    return prompts
##new ui ends##


@api_view(["POST"])
def agentic_hub(request):
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        agentic_data = json.dumps(request.data)
        print(agentic_data,"##$$%%%%%%%%%")
        data_json = json.loads(agentic_data)
        model_names = extract_model_name(data_json)
        model_names = [item for item in model_names if item is not None]
        agent_name = request.data.get("projectName")
        project_type = request.data.get("projectType")
        prompt_text = get_prompts_from_models(data_json['nodes'])
        print(prompt_text,"###$$")
        if model_names[0]:
            model_name = model_names[0]
            print(model_name,"$$$$$$$")
        else:
            result = {"status": "0", "message": "No Model is selected"}
            return JsonResponse(result, safe=False)
        
        config_add = add_fields_configuration_prompt(user_id, company_code, agent_name, prompt_text[0], model_name, agent_name, project_type)
        print('yesss')
        agentic_instance = AgenticItems()
        try:
            # Check if the project exists
            if agentic_instance.is_project_exist(company_code, agent_name):
                result = {"status": "0", "message": "Project already exists"}
                return JsonResponse(result, safe=False)
            else:
                # If not, save the project data
                agentic_instance.save_agent_data(user_id, company_code, agent_name, agentic_data)
                result = {"status": "1", "message": "Project created successfully"}
                return JsonResponse(result, safe=False)
                
        except Exception as e:
            traceback.print_exc()
            error_message = {"status": "0", "message": str(e)}
            return JsonResponse(error_message, safe=False)
    
    # If user is not authenticated
    result = {"status": "0", "message": "You are not authorized to access."}
    return JsonResponse(result, safe=False)

@api_view(["POST"])
def get_agent_data(request):
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        agentic_data = request.data
        print(agentic_data,"$$$$")
        agent_name = agentic_data['projectName']
        agentic_instance = AgenticItems()
        result = agentic_instance.get_agentic_data(user_id, company_code, agent_name)
        print(result[0]['agent_data'],"@@@@@@@@@@@@@@@@@@@@@@")
        
        return JsonResponse(result, safe=False)
        
    
    # If user is not authenticated
    result = {"status": "0", "message": "You are not authorized to access."}
    return JsonResponse(result, safe=False)
    


@api_view(["POST"])
def get_configuration_agent_data(request):

    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        agentic_data_raw = request.data
        
        agentic_data = agentic_data_raw['projectData']
        print(agentic_data,"@@###")
        agent_name = agentic_data.get('projectName')
        if not agent_name:
            error = {"error": "Project name is required"}
            return JsonResponse(error)

        obj = customfields()
        print(agent_name,"##$$$")
        header, table = obj.get_fields_prompt(agent_name, company_code)
        
        if header or table:
            header = {d['field_key']: d['mapped_prompt'] for d in header} if header else {}
            table = {d['field_key']: d['mapped_prompt'] for d in table} if table else {}
            dynamic_prompt_data = {"header": header, "line_items": table}
        else:
            dynamic_prompt_data = {}

        response_data = {"dynamic_prompt_data": dynamic_prompt_data}
        return JsonResponse(response_data)
    else:
        error = {"error": "Unauthorized"}
        return JsonResponse(error)
       
        
    
    # If user is not authenticated
    result = {"status": "0", "message": "You are not authorized to access."}
    return JsonResponse(result, safe=False)

def get_all_agent_data(request):
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        agentic_instance = AgenticItems()
        result = agentic_instance.get_all_agentic_data(user_id, company_code)
        result = [dict(item) for item in result]
        print(result,"*************************")
        return JsonResponse(result, safe=False)
        
    
    # If user is not authenticated
    result = {"status": "0", "message": "You are not authorized to access."}
    return JsonResponse(result, safe=False)

@api_view(["GET"])
def get_project_names(request):
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        agentic_instance = AgenticItems()
        result = agentic_instance.get_project_name(user_id, company_code)
        project_names = [item['agent_name'] for item in result]
        project_id = [item['id'] for item in result]
        print(project_names,"@@@@@@@@@@@@@@@@@")

        print(project_id,"@@@@@@@@@@@@$$$$$$$$$$$$$$$$@@@@@")
        return JsonResponse(project_names, safe=False)
        
    
    # If user is not authenticated
    result = {"status": "0", "message": "You are not authorized to access."}
    return JsonResponse(result, safe=False)

@api_view(["POST"])
def run_agentic_project(request):
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        agentic_data = request.data
        print(agentic_data,"$$$$")
        ##BACKEND RUNNING DATA ##

        ##ENDS##
        print(agentic_data,"@@@@@@@@@@@@@@@@@@@@@@11111111111111111111111")
        
        return JsonResponse(agentic_data, safe=False)
        
    
    # If user is not authenticated
    result = {"status": "0", "message": "You are not authorized to access."}
    return JsonResponse(result, safe=False)
    
@api_view(["POST"])
def delete_project(request):
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        agentic_data = request.data
        agentic_instance = AgenticItems()
        agent_name = agentic_data['projectName']
        result = agentic_instance.delete_project(user_id, company_code, agent_name)
        return JsonResponse(agentic_data, safe=False)
        
    
    # If user is not authenticated
    result = {"status": "0", "message": "You are not authorized to access."}
    return JsonResponse(result, safe=False)

@api_view(["POST"])
def update_agentic_project(request):
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        project_data = request.data
        agent_name = project_data['projectName']
        project_data = json.dumps(project_data)
        agentic_instance = AgenticItems()
        
        result = agentic_instance.update_project(user_id, company_code, project_data, agent_name)
        result = {"status": "1", "message": "Project updated succesfully"}
        return JsonResponse(result, safe=False)
        
    
    # If user is not authenticated
    result = {"status": "0", "message": "You are not authorized to access."}
    return JsonResponse(result, safe=False)


@api_view(["POST"])
def update_agentic_project_running_status(request):
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        project_data = request.data
        print(project_data,"##$$%%%%%%%%%%%%%%%%%%%%")
        agent_name = project_data['projectName']
        running_status = project_data['status']
        print(running_status,"@EEEEEE")
        if running_status:
            running_status = '1'
        else:
            running_status = '0'
        agentic_instance = AgenticItems()
        
        result = agentic_instance.update_running_status(user_id, company_code, agent_name, running_status)
        result = {"status": "1", "message": "Project status updated succesfully"}
        return JsonResponse(result, safe=False)
        
    
    # If user is not authenticated
    result = {"status": "0", "message": "You are not authorized to access."}
    return JsonResponse(result, safe=False)


@api_view(["POST"])
def get_agentic_project_running_status(request):
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        project_data = request.data
        print(project_data,"--------------------------")
        agent_name = project_data['projectName']
        agentic_instance = AgenticItems()
        
        result = agentic_instance.get_running_status(user_id, company_code, agent_name)
        result = result[0].get('running_status')
        if result is True or result == '1':
            result = 'running'
        else:
            result = 'stopped'
        result = {"projectName": agent_name, "status": result}
        print(result,"##$$")
        return JsonResponse(result, safe=False)
        
    
    # If user is not authenticated
    result = {"status": "0", "message": "You are not authorized to access."}
    return JsonResponse(result, safe=False)

def get_agent_process_live_status(request):
    agentic_instance = AgenticItems()
    result = agentic_instance.fetch_unprocessed_files()
    print(result,"!@@@####")
    return JsonResponse(result, safe=False)

def get_user_from_session(request): 
     return str(request.session['user_id'])

def get_company_code_from_session(request): 
     return str(request.session['company_code'])