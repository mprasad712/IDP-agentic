import uuid
import shutil
import ast
import requests
import os

from django.shortcuts import render 
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import * 
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
import traceback

import pandas as pd

from django.contrib.auth import logout as django_logout
from django.views.decorators.cache import cache_control 
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate
import calendar;
import time;


from invoiceapp.business_logic.site_settings import site_settings
from invoiceapp.business_logic.customfields import customfields
from invoiceapp.business_logic.processed_items import processed_items
from invoiceapp.business_logic.audited_items import audited_items
from invoiceapp.business_logic.predicted_items import predicted_items
from invoiceapp.business_logic.audited_itemdetails import audited_itemdetails
from invoiceapp.business_logic.accuracy_items import accuracy_items
from invoiceapp.business_logic.invoice_upload import invoice_upload
from invoiceapp.business_logic.dashboard_items import dashboard_items
from invoiceapp.business_logic.deleted_invoice import deleted_invoice
from invoiceapp.business_logic.issue_report import issue_report
from invoiceapp.business_logic.users import users
from invoiceapp.business_logic.agentic_items import AgenticItems

from  invoiceapp.business_logic.calculate_accuracy  import init_accuracy
from datetime import date, datetime,timedelta
from django.contrib.auth import authenticate, login
from invoiceapp.business_logic.email_provider import email_provider
from rest_framework.response import Response


agentic_instance = AgenticItems()


@api_view(["POST"])
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def loginprocess(request):
    dictData = {}
    user_info = request.data.get("userInfo", {})
    
    username = user_info.get('username')
    password = user_info.get('password')
    prod_mode = user_info.get('prod_mode')
    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)
        request.session["user_id"] = user.id
        request.session["first_name"] = user.first_name
        request.session["first_letter"] = user.first_name[0]
        request.session["last_name"] = user.last_name
        request.session["last_letter"] = user.last_name[0]
        request.session["email"] = user.email
        request.session["WEB_API_LINK"] = settings.WEB_API_LINK
        request.session["prod_mode"] = prod_mode
        _objUser = users.get_user_info(request.session["user_id"])
        request.session["user_profle_image"] = _objUser[0]["profile_img"]
        request.session["user_org_image"] = _objUser[0]["org_img"]
        request.session["is_local_admin"] = _objUser[0]["is_local_admin"]
        request.session["company_code"] = _objUser[0]["company_code"]
        print(user.id,_objUser[0]["company_code"],"+++")
        responsedict = {"status": "1", "Message": "Logged in successfully.", "first_name": user.first_name, "last_name": user.last_name, "first_letter": user.first_name[0], "last_letter": user.last_name[0]}
        return HttpResponse(json.dumps(responsedict))
    else:
        responsedict = {"status": "0", "Message": "Invalid login."}
        return HttpResponse(json.dumps(responsedict))

def copy_agent_to_company(user_id, company_code, agent_name, agentic_data):
    try:
        agent_data_json = json.dumps(agentic_data)
        agentic_instance.save_agent_data(user_id, company_code, agent_name, agent_data_json)
    except:
        responsedict = {"status": "0", "Message": "Error Occured - Default Agent Creation Error"}
        return HttpResponse(json.dumps(responsedict))

@api_view(["POST"])
def registeruser(request):
    username = '';
    company_name= ''
    password= '';
    first_name = '';
    last_name = '';
    email = '';
    cpassword = '';
    is_staff = '' ;
    contact_email = '';
    dictData = {}    
    # dictData = request.data.get("userInfo", {})
    dictData=request.data["userInfo"]
    try:
        UUID =  str(uuid.uuid4().hex[:8])

        auth_code =  str(uuid.uuid4())
        auth_pin =  str(uuid.uuid4().hex[:8])
        
        username = dictData['new_email']
        password = make_password(dictData['new_password'])
        u_encrypt_pass = ''
        first_name = dictData['new_first_name']
        last_name= dictData['new_last_name']
        email = dictData['new_email']
        # company_name= dictData['new_org_name']
        is_staff = dictData['new_is_superuser']
        is_outer_user = dictData['is_outer_user']
        if(is_outer_user == "outer"):
             company_code = UUID
             contact_email = ''
        else:
             company_code = get_company_code_from_session(request)
             contact_email = ''

        profile_img = "demo_img.png"
        
        if(users.is_user_exist(email) == True):
            responsedict = {"status":"0","Message" : email + " already registered with us!"}
            return HttpResponse(json.dumps(responsedict))
        else:
            result = users.create_new_user(username,password,first_name,last_name,email,company_name,is_staff,profile_img,company_code,contact_email,auth_code,auth_pin,u_encrypt_pass)
            users.insert_organization_detail(result,"",company_name,"","","","","")   

            # Linking Admin Page for Agentic AI
            try:
                current_company_code = company_code
                user_agents = agentic_instance.get_all_agentic_data(result, current_company_code)  
                user_agents = [json.loads(agent['agent_data']) for agent in user_agents]
                target_company_code = '5b94acb0'
                target_user_id = '22387'
                target_agents = agentic_instance.get_all_agentic_data(target_user_id, target_company_code)  
                target_agents = [json.loads(agent['agent_data']) for agent in target_agents]
                user_agent_names = {agent['projectName'] for agent in user_agents}
                target_agent_names = {agent['projectName'] for agent in target_agents}
                agents_to_copy = [agent for agent in target_agents if agent['projectName'] not in user_agent_names]
                
                for agent in agents_to_copy:
                    copy_agent_to_company(result, current_company_code, agent['projectName'], agent)
            except Exception as e:
                print(e,"@@###############")
                
            # Ends
            responsedict = {"status":"1","Message" : "User created successfully. Please check your registered email and confirm."}
            return HttpResponse(json.dumps(responsedict))
        
    except Exception as e:
        print("Excepption",e)
        responsedict = {"status":'0',"Message" : "Invalid information Please check entered details."}
        return HttpResponse(json.dumps(responsedict))
        

@api_view(['POST'])
def extracted_fields_idp(request): 
    user_id = get_user_from_session(request)
    company_code = get_company_code_from_session(request)
    
    dictData = {}  
    dictData = request.data
    # print(dictData,"+++")
    UUID = dictData.get("UUID")
    
    is_detail = dictData.get("is_detail", "0")
    # print(dictData)
    
    item_status = "2"
    if is_detail == "0":

        status = processed_items.is_inprogress(UUID, user_id)

        if str(status[0]["user_id"]) == str(user_id):
            # print("444")
            item_status = "1"

        else:
            item_status = status[0]["predicted_status"]
    else:
        item_status = "1"
    
    if item_status == "1":

        if is_detail == "0":
            processed_items.update_predict_status(UUID, "2", user_id)

        obj_predictedData = predicted_items() 

        config_id = obj_predictedData.get_config_uuid(UUID)

        customfields = get_fields(user_id, config_id, company_code)
        result = {'customfields': customfields, 'status': 'success', 'message': ''}
        print(result,"11111")
        return JsonResponse(result, safe=False)
    else:
        result = {
            'customfields': {},
            'status': 'info',
            'message': f'Record is already being processed by <b>{status[0]["first_name"]} {status[0]["last_name"]}</b>'
        }
        print(result,"2222")
        return JsonResponse(result, safe=False)



@api_view(['POST'])
def get_audited_data(request):  
    user_id = get_user_from_session(request)
    company_code = get_company_code_from_session(request)
    
    dictData = {} 
    dictData = request.data
    UUID = dictData.get("UUID")
    # print("UUID", UUID)
    obj_audited_itemdetails = audited_itemdetails() 
    standard_result = obj_audited_itemdetails.get_standard_data(UUID,"",user_id,company_code)

    table_data = obj_audited_itemdetails.get_table_data(UUID,"",user_id,company_code)
   
    result = {"standard_data" : standard_result, "table_data": table_data}
    print(result,"***")
    return  JsonResponse(result,safe=False) 

@api_view(['POST'])
def get_predict_data(request): 
    user_id = get_user_from_session(request)
    company_code = get_company_code_from_session(request)
    dictData = {}     
    dictData = request.data
    UUID = dictData.get("UUID") 
    obj_predictedData = predicted_items() 
    standard_result = obj_predictedData.get_standard_data(UUID,"",user_id,company_code) 
    table_data = obj_predictedData.get_table_data(UUID,"",user_id,company_code)
    next_id = obj_predictedData.get_next_id(UUID,user_id,company_code)
    result = {"standard_data" : standard_result, "table_data": table_data,"next_id":next_id }
    
    return  JsonResponse(result,safe=False) 

@api_view(["POST"])
def auditSubmit(request):
    user_id = get_user_from_session(request)
    company_code = get_company_code_from_session(request)
    try:
        dictData = request.data
        print(dictData, "@@@")
        
        # Parse 'auditInfo' JSON string into a dictionary
        audit_info = json.loads(dictData['auditInfo'])
        
        StandardFieldList = audit_info['StandardFieldList']
        rowHeaderList = audit_info['rowHeaderList']
        rowColumnList = audit_info['rowColumnList']
        predicted_uuid = audit_info['predicted_uuid']

        is_exist = audited_items.is_item_exist(predicted_uuid)

        obj_predictedData = predicted_items()
        config_id = obj_predictedData.get_config_uuid(predicted_uuid)
        file_uuid = obj_predictedData.get_file_uuid(predicted_uuid)

        if is_exist:
            ret_dict = {'status': "0", 'message': 'File already audited.'}
            return HttpResponse(json.dumps(ret_dict))
        else:
            if user_id:
                result = audited_items.file_audit_submit(
                    user_id, StandardFieldList, rowHeaderList, rowColumnList, 
                    predicted_uuid, config_id, file_uuid, company_code
                )
                audited_items.update_audit_status(predicted_uuid, "3")
                invoice_upload.updated_by_UUID(file_uuid, '3')

                init_accuracy(user_id, "", file_uuid, datetime.now().date(), datetime.now().date(), predicted_uuid, company_code)
                ret_dict = {'status': "1", 'message': 'audited successfully'}
                return HttpResponse(json.dumps(ret_dict))

    except Exception as e:
        traceback.print_exc()
        # Ensure predicted_uuid is initialized to avoid UnboundLocalError
        try:
            audited_items.roll_back_audit_item(predicted_uuid)
            audited_items.update_audit_status(predicted_uuid, "1")
            audited_items.update_audit_status(predicted_uuid, "4")
        except Exception as rollback_exception:
            print(f"Error during rollback: {rollback_exception}")

        print(str(e))
        ret_dict = {'status': "0", 'message': 'Invalid Data, Please try again'}
        return HttpResponse(json.dumps(ret_dict))

# @api_view(["POST"]) 
# def add_fields_configuration(request):
#     print(request.data,"-----")
    
#     user_id = get_user_from_session(request)
#     company_code = get_company_code_from_session(request)
#     objcustom  = customfields()
#     if not objcustom.validate_layout_count(user_id,company_code):
#         result = {"status":"0" ,"message":"You have reached to add max laypout."} 
#         print(result)
#         return JsonResponse(result,safe=False)
         
#     dictData = {}    
#     # dictData = ast.literal_eval(request.data["field_info"])
#     print(request.data,"-----")
#     dictData=request.data["field_info"]
#     configuration_name = dictData["config_name"]
#     static_fields = dictData["standard_dict"]
#     static_custom_fields = dictData["custom_dict"]
#     static_custom_datatype = dictData["custom_dict_datatype"]
#     table_static_fields = dictData["table_static_dict"]
#     table_custom_fields = dictData["table_custom_dict"]
#     table_custom_fields_mapping_name = dictData["table_custom_fields_mapping_name"]
#     custom_dict_mapping = dictData["custom_dict_mapping"]

#     datatype_custom_dict =  dictData["datatype_custom_dict"]
#     datatype_standard_dict =  dictData["datatype_standard_dict"] 

#     try:
        
#         if(objcustom.is_config_exist(company_code,configuration_name) ==  True):
#             result = {"status":"0","message":"Configuration already exist"}
#             return JsonResponse(result,safe=False) 
#         else:
#             UUID =  configuration_name.replace(" ","_").lower()
            
#             output  = objcustom.add_standard_fields_config(UUID,user_id,datatype_standard_dict,datatype_custom_dict,table_static_fields,table_custom_fields,configuration_name,static_custom_datatype,company_code)
#             print("ddddddddddddddd")
#             if(output == "Miscellaneous Action found"):
#                 result = {"status":"0" ,"message":"Miscellaneous Action found."}
#             else:       create_user_folder(user_id,UUID,static_fields,custom_dict_mapping,table_static_fields,table_custom_fields,static_custom_fields,static_custom_datatype,table_custom_fields_mapping_name,company_code)
#             result = {"status":"1" ,"message":"Configuration created successfully."} 
#             return JsonResponse(result,safe=False)  
#     except Exception as e:
#         traceback.print_exc()
#         print(str(e))

@api_view(["POST"]) 
def add_fields_configuration(request):
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        print(company_code)
        objcustom  = customfields()
        if not objcustom.validate_layout_count(user_id,company_code):
            result = {"status":"0" ,"message":"You have reached to add max laypout."} 
            print(result)
            return JsonResponse(result,safe=False)
             
        dictData = {}    
        dictData = ast.literal_eval(request.data["field_info"])
        configuration_name = dictData["config_name"]
        static_fields = dictData["standard_dict"]
        static_custom_fields = dictData["custom_dict"]
        static_custom_datatype = dictData["custom_dict_datatype"]
        table_static_fields = dictData["table_static_dict"]
        table_custom_fields = dictData["table_custom_dict"]
        table_custom_fields_mapping_name = dictData["table_custom_fields_mapping_name"]
        custom_dict_mapping = dictData["custom_dict_mapping"]

        datatype_custom_dict =  dictData["datatype_custom_dict"]
        datatype_standard_dict =  dictData["datatype_standard_dict"] 
        prompt_custom_dict = dictData.get("prompt_custom_dict", []) 
        prompt_table_custom_dict = dictData.get("prompt_table_custom_dict", []) 

        try:
            
            if(objcustom.is_config_exist(company_code,configuration_name) ==  True):
                result = {"status":"0","message":"Configuration already exist"}
                return JsonResponse(result,safe=False) 
            else:
                UUID =  configuration_name.replace(" ","_").lower()
                
                output  = objcustom.add_standard_fields_config(UUID,user_id,datatype_standard_dict,datatype_custom_dict,table_static_fields,table_custom_fields,prompt_custom_dict, prompt_table_custom_dict, configuration_name,static_custom_datatype,company_code) 
                if(output == "Miscellaneous Action found"):
                    result = {"status":"0" ,"message":"Miscellaneous Action found."}
                else:
                    create_user_folder(user_id,UUID,static_fields,custom_dict_mapping,table_static_fields,table_custom_fields,static_custom_fields,static_custom_datatype,table_custom_fields_mapping_name,company_code)
                    if prompt_custom_dict or prompt_table_custom_dict:
                        header, table = objcustom.get_fields_prompt(UUID, company_code)
                        create_json_file(header, table, UUID)
                    result = {"status":"1" ,"message":"Configuration created successfully."} 
                return JsonResponse(result,safe=False)  
        except Exception as e:
            print(str(e))
    else:
        result = {"status":"0" ,"message":"You are not authorized to access."} 
        return JsonResponse(result,safe=False) 


def add_fields_configuration_prompt(user_id, company_code, configuration_name, prompt_text, model_name, agent_name, project_type):
    objcustom  = customfields()
    if not objcustom.validate_layout_count(user_id,company_code):
        result = {"status":"0" ,"message":"You have reached to add max laypout."} 
        print(result)
        return JsonResponse(result,safe=False)
    
    static_fields = ["file_name"]
    static_custom_fields = []
    static_custom_datatype = []
    table_static_fields = []
    table_custom_fields = []
    table_custom_fields_mapping_name = []
    custom_dict_mapping = []

    datatype_custom_dict =  []
    datatype_standard_dict =  ["file_name|text"]
    prompt_custom_dict = []
    prompt_table_custom_dict = []
    serialized_prompt_text = prompt_text
    data = {"user_prompt": serialized_prompt_text, "model_name":model_name, "agent_name": agent_name, "user_id": user_id, "project_type": project_type}
    try:
        print(data,"$%%^^TTTT")
        response = requests.post(url = settings.META_PROMPT_API_LINK, json=data)
        response = response.json()
        print(response,"@@#$$$$$$$$$$$$$$$$$$$$___________________")
    except Exception as e:
        traceback.print_exc()
        result = {"status":"0" ,"message":"Miscellaneous Action found."}
        return JsonResponse(result,safe=False)

    static_custom_fields = response.get("custom_dict", [])
    prompt_custom_dict = response.get("prompt_custom_dict", [])
    table_custom_fields = response.get("table_custom_dict", [])
    prompt_table_custom_dict = response.get("prompt_table_custom_dict", [])

    for i in range(1, len(static_custom_fields)+1):
        custom_dict_mapping.append(f"s_{i}")
        static_custom_datatype.append("text")
        datatype_custom_dict.append(f"{static_custom_fields[i-1]}|text")

    for j in range(1, len(table_custom_fields)+1):
        table_custom_fields_mapping_name.append(f"t_{j}")

    try:
        
        if(objcustom.is_config_exist(company_code,configuration_name) ==  True):
            result = {"status":"0","message":"Configuration already exist"}
            return JsonResponse(result,safe=False) 
        else:
            UUID =  configuration_name.replace(" ","_").lower()
            
            output  = objcustom.add_standard_fields_config(UUID,user_id,datatype_standard_dict,datatype_custom_dict,table_static_fields,table_custom_fields,prompt_custom_dict, prompt_table_custom_dict, configuration_name,static_custom_datatype,company_code, str(prompt_text).replace("'", '"')) 
            if(output == "Miscellaneous Action found"):
                result = {"status":"0" ,"message":"Miscellaneous Action found."}
            else:
                create_user_folder(user_id,UUID,static_fields,custom_dict_mapping,table_static_fields,table_custom_fields,static_custom_fields,static_custom_datatype,table_custom_fields_mapping_name,company_code)
                
                result = {"status":"1" ,"message":"Configuration created successfully."} 
            return JsonResponse(result,safe=False)  
    except Exception as e:
        traceback.print_exc()
        print(str(e))
        
@api_view(["POST"]) 
def delete_field_config(request):
    try:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        print(user_id,"ssddddddd")
        dictData = {} 
        dictData = request.data
        print(dictData,"4444")
        configuration_uuid = dictData["config_uuid"] 
        print(configuration_uuid,"######")
        objcustom  = customfields()
        objcustom.delete_config(user_id,configuration_uuid)
        print("Deleting Config")
        #print("path@@@@@@@@@@@@@@@@@@@@@@@@@",settings.ACTIVE_LEARNING_ROOT + str(company_code) + "/" + str(configuration_uuid)) 
        if os.path.exists(settings.ACTIVE_LEARNING_ROOT + str(company_code) + "/" + str(configuration_uuid)):
            shutil.rmtree(settings.ACTIVE_LEARNING_ROOT + str(company_code) + "/" + str(configuration_uuid))

        if os.path.exists(settings.SOLUTION_OUTPUT_DATA + str(company_code) + "/" + str(configuration_uuid)):
            shutil.rmtree(settings.SOLUTION_OUTPUT_DATA + str(company_code) + "/" + str(configuration_uuid))

        if os.path.exists(settings.INVOICE_DATA_ROOT + str(company_code) + "/" + str(configuration_uuid)):
            shutil.rmtree(settings.INVOICE_DATA_ROOT +  str(company_code) + "/" + str(configuration_uuid))
         


        result = {"status":"1","message":"Layout deleted successfully."}
        return JsonResponse(result,safe=False)
    except Exception as e:
        print(e)
        result = {"status":"0","message":"Error Please try again."}
        return JsonResponse(result,safe=False)

@api_view(["POST"])
def addsupplier(request):
    dictData = {}    
    dictData = ast.literal_eval(request.data["suppInfo"])
    supplier_id = dictData['supplier_id']
    supplier_name = dictData['supplier_name']
    supplier_status = dictData['supplier_status']
    company_code = get_company_code_from_session(request)
    try:
        result = users.addsupplier(supplier_id,supplier_name,supplier_status,company_code)
        print("Company Name",company_name)
        users.insert_organization_detail(result,"",company_name,"","","","","")   

            #obj_email = email_provider()
            #obj_email.sent_mail(UUID, username,first_name, last_name,email,"",auth_pin,auth_code)

        responsedict = {"status":"1","Message" : "Supplier addedsuccessfully."}
        return HttpResponse(json.dumps(responsedict))
    except Exception as e:
        print("Excepption",e)
        responsedict = {"status":'0',"Message" : "Invalid information Please check entered details."}
        return HttpResponse(json.dumps(responsedict)) 


      
      
def create_user_folder(user_id, config_id,static_fields,static_custom_fields,table_static_fields,table_custom_fields,static_custom_fields_mapping,static_custom_datatype,table_custom_fields_mapping_name,company_code):
    #print("you are creating folders")
    if not os.path.exists(settings.INVOICE_DATA_ROOT + "/"+ str(company_code)):
                os.makedirs(settings.INVOICE_DATA_ROOT + "/"+ str(company_code))

    if not os.path.exists(settings.INVOICE_DATA_ROOT + "/"+ str(company_code) + "/"+ str(config_id)):
                os.makedirs(settings.INVOICE_DATA_ROOT + "/"+ str(company_code)+ "/"+ str(config_id)) 

    try:
        create_user({'user_id':str(company_code)})
    except Exception as e:
        pass
    #print("Creating User Config")
    input_dict = {
    'user_id' : str(company_code),
    'user_uuid':str(config_id),
    'standard' : static_fields,
    'standard_custom' : static_custom_fields,
    'table' : table_static_fields,
    'table_custom': table_custom_fields,    
    'static_custom_fields_mapping_name': static_custom_fields_mapping,
    'table_custom_fields_mapping_name': table_custom_fields_mapping_name,
    'custom_static_datatype': static_custom_datatype}




def get_user_from_session(request): 
    print(dict(request.session), "####")

    return str(request.session['user_id'])

def get_company_code_from_session(request): 
     return str(request.session['company_code'])

 
def get_fields(user_id,config_id,company_code):
    objcustom  = customfields()
    result = objcustom.get_custom_fields(user_id,config_id,company_code) 
    # print(result,"mmmmmmmmmmmmmmmm")
    return result


def output_excel_from_ui(data):

    file_name = data['StandardFieldList']['file_name']
    file_name = file_name.replace('.pdf','.xlsx').replace('.PDF','.xlsx')
    excel_path = r'/mnt/share/ocr_output/' + file_name
    standard_data = {
        'File Name': data['StandardFieldList']['file_name'],
        'Po Number': data['StandardFieldList']['po_number'],
        'Po Date': data['StandardFieldList']['invoice_date'],
        'Vendor Address': data['StandardFieldList']['bill_to_address'],
        'Ship To Address': data['StandardFieldList']['ship_to_address'],
        'Gst Number': data['StandardFieldList']['gst_number'],
        'Expiry Date': data['StandardFieldList']['s_1']

    }
    standard_df = pd.DataFrame(standard_data,index=[0])

    # Create DataFrame for the second sheet
    line_item_df = pd.DataFrame(data['rowColumnList'], columns=['Description', 'Unit Price', 'Quantity', 'EAN No', 'Article No', 'HSN Code', 'Pack', 'Total Amount', 'Taxable Amount'])

    # Create Excel writer object
    with pd.ExcelWriter(excel_path) as writer:
        # Write DataFrames to sheets
        standard_df.to_excel(writer, sheet_name='Headers', index=False)
        line_item_df.to_excel(writer, sheet_name='Line Items', index=False)

    return True

    
@api_view(["POST"])
def deletedprocessedRecords(request):
    if 'user_id' in request.session:
        try:
            dictData = {}    
            dictData = request.data["userInfo"]
            print(dictData,"++___***")
            user_id = get_user_from_session(request)
            id = dictData["Id"]    
            item_status = "1" # Default
            status = processed_items.is_inprogress(id,user_id)
            item_status =  status[0]["predicted_status"]
            print(item_status)
            if item_status == "1":
                res = deleted_invoice.invoice_delete(user_id,id)  
                result = {}  
                result["id"] = id
                result["status"] = "1"
                result["message"] = "Deleted Successfully."
                return  JsonResponse(result,safe=False)
            else:
                result["id"] = id
                result["status"] = "0"
                result["message"] = "Document is already being processed by another user."
                return JsonResponse(result,safe=False)
             
             
        except Exception as e:
            print(str(e))
            result = {}  
            result["id"] = id
            result["status"] = "0"
            result["message"] = "Something went wrong, Please try again."
            return  JsonResponse(result,safe=False)
    else:
        result = {}  
        result["id"] = id
        result["status"] = "0"
        result["message"] = "Something went wrong, Please try again."
        return  JsonResponse(result,safe=False)
        
