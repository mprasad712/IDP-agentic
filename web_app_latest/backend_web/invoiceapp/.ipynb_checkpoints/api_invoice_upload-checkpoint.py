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
from flask import jsonify
from django.views.decorators.csrf import csrf_exempt 
from django.core.serializers.json import DjangoJSONEncoder
import shutil 

from django.contrib.auth import logout as django_logout
from django.views.decorators.cache import cache_control 
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate
import calendar;
import time;
from datetime import datetime


# Business Libraries
from invoiceapp.business_logic.site_settings import site_settings
from invoiceapp.business_logic.customfields import customfields
from invoiceapp.business_logic.processed_items import processed_items
from invoiceapp.business_logic.audited_items import audited_items
from invoiceapp.business_logic.predicted_items import predicted_items
from invoiceapp.business_logic.audited_itemdetails import audited_itemdetails
from invoiceapp.business_logic.accuracy_items import accuracy_items
from invoiceapp.business_logic.invoice_upload import invoice_upload
from invoiceapp.business_logic.users import users
from invoiceapp.business_logic.dashboard_items import dashboard_items
from invoiceapp.business_logic.deleted_invoice import deleted_invoice
from invoiceapp.business_logic.issue_report import issue_report
from invoiceapp.business_logic.agentic_items import AgenticItems


@api_view(["POST"])
def is_upload_allow(request):
    #print("InSide Upload")
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        count_file = invoice_upload.file_uploaded_count(user_id,company_code) 
        
        '''if(int(settings.MAX_FILE_COUNT)  <= int(count_file)):
            result = {"status":"0","message":"You have reached upto max limit of file upload."}
            return JsonResponse(result,safe=False)
        else:
            result = {"status":"1","message":""} 
            return JsonResponse(result,safe=False)'''
        result = {"status":"1","message":""} 
        return JsonResponse(result,safe=False)
    else:
        result = {"status":"0","message":"You are not authorized to access."}
        return JsonResponse(result,safe=False)



@api_view(["POST"]) 
def delete_invoice_file(request):
    if 'user_id' in request.session:
        dictData = {}    
        dictData = ast.literal_eval(request.data["file_info"])
        user_id =  str(request.session['user_id'])
        file_name = dictData["file_name"]
        file_id = dictData["file_id"]  
        company_code = get_company_code_from_session(request) 

        #print("Deleting file",file_id)

        config_uuid = invoice_upload.get_config_uuid(file_id) 
        invoice_path = os.path.join(settings.INVOICE_DATA_ROOT,company_code,config_uuid,file_name) 
        #print("Invoice Path", invoice_path)
        try:
            # DELETE FILE FROM DATABASE
            invoice_upload.delete_by_ID(file_id)

            # Delete file from Folders
            if os.path.exists(invoice_path):
                os.remove(invoice_path)
            result = {"message" : "Success","file_id" : file_id}              
            return JsonResponse(result,safe=False) 
        except Exception as e:             
            result = {"message" : "Error","file_id" : file_id}              
            return JsonResponse(result,safe=False)
    else:
        result = {"message" : "You are not authorized to access","file_id" : file_id}              
        return JsonResponse(result,safe=False)




UPLOAD_FOLDER = '/data/digital_workmate/idp/idp/input_folder'

UPLOAD_VOICE_FOLDER = '/data/digital_workmate/idp/idp/input_folder/voice_data/training_data_voice'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG','wav','mp3'}
def upload_ricefile(request):
    try: 
        filename = request.FILES['file'].name
        data = request.FILES['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if filename == '':
            return  jsonify({"error_code": "501","error_message": "File is missing from source or "})   
        if allowed_file(filename):
            try:
                tmp_file = os.path.join(UPLOAD_FOLDER, filename)  #os.path.join(os.getcwd() + "/upmapp/static/","DownloadFolder", filename)
                path = default_storage.save(tmp_file, ContentFile(data.read()))
                #print("path",tmp_file)
                data = {'file_name':filename}
                response = requests.post(url = settings.API_RICELINK, data = data)
                responseObj = response.json()
                print("dsfdsfdsf",responseObj)
                return JsonResponse(responseObj,safe=False)
            except Exception as e:
                print("error occure",e)        
        else:
            return  jsonify({"error_code": "501","error_message": "File formate is not allowed."})   
    except Exception as e:
        print(e)
        return jsonify({"error_code": "500","error_message": "Internal Server Error"})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_voicefile(request):
    try: 
        filename = request.FILES['file'].name
        data = request.FILES['file']
        print(filename)
        print(data)
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if filename == '':
            return  jsonify({"error_code": "501","error_message": "File is missing from source or "})   
        if allowed_file(filename):
            try:
                tmp_file = os.path.join(UPLOAD_VOICE_FOLDER, filename)  #os.path.join(os.getcwd() + "/upmapp/static/","DownloadFolder", filename)
                path = default_storage.save(tmp_file, ContentFile(data.read()))
                result =  {"message" : "Registration Successfully"} 
                return JsonResponse(result,safe=False) 
            except Exception as e:
                print("error occure",e)        
        else:
            return  jsonify({"error_code": "501","error_message": "File formate is not allowed."})   
    except Exception as e:
        print(e)
        return jsonify({"error_code": "500","error_message": "Internal Server Error"})

@api_view(["POST"])
# @csrf_exempt
def uploadfile(request):
    try:
        
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        dictData = {}  
        project_name = request.POST.get('projectName', None)
        print(project_name,"@@##")
        filename = request.FILES['file'].name
        config_id = project_name
        ocr_id = '1'
        ocr_id = request.POST.get('ocr_id',None)
        source_code = request.POST.get('source_code',None)
        engine_id = request.POST.get('engine_id',None)
        doc_id = request.POST.get('doc_id',None)
        data = request.FILES['file']
        agentic_instance = AgenticItems()
        
        print("****************************************************************************")

        try:  
            tmp_file = os.path.join(settings.FILES_DIR,company_code,config_id, filename)  
            path = default_storage.save(tmp_file, ContentFile(data.read()))
            filename = os.path.basename(path)
            bulk_temp_path = shutil.copy2(path, f'/data/digital_workmate_agentic/input_queue/{user_id}/{project_name}/')
            agentic_instance.save_upload_data(user_id, company_code, project_name, filename)
        except Exception as e:
            print("Exception In Code :",str(e))     

        process_by = "Pradeep Yadav"
        
        result =  {"message" : "Uploaded Successfully"} 
        return JsonResponse(result,safe=False)
    except Exception as e:
        result =  {"status" : "0", "message" : "Error Some thing went wrong, Please try again","uuid" : "0" } 
        return JsonResponse(result,safe=False)

@api_view(["POST"])
# @csrf_exempt
def uploadmultiplefiles(request):
    try:
        # Retrieve user and company information from the session
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)

        # Extract additional information from the request
        project_name = request.POST.get('projectName', None)
        config_id = project_name  # Assuming this is correct as per your context
        ocr_id = request.POST.get('ocr_id', '1')
        source_code = request.POST.get('source_code', None)
        engine_id = request.POST.get('engine_id', None)
        doc_id = request.POST.get('doc_id', None)

        # Get the list of uploaded files
        files = request.FILES.getlist('files')
        print(files,"__")
        if not files:
            return JsonResponse({"status": "0", "message": "No files uploaded."}, safe=False)

        # Iterate over each file and process them
        for file in files:
            filename = file.name
            data = file
            print(file,"**")

            try:
                # Construct the file path
                tmp_file = os.path.join(settings.FILES_DIR, company_code, config_id, filename)

                # Save the file
                path = default_storage.save(tmp_file, ContentFile(data.read()))
                
                # Copy the file to another directory
                bulk_temp_path = shutil.copy2(path, f'/data/digital_workmate_agentic/input_queue/{user_id}/{project_name}/')
                

            except Exception as e:
                print("Exception In Code:", str(e))
                return JsonResponse({"status": "0", "message": f"Error processing file {filename}. Please try again."}, safe=False)

            # Optional: Insert data into the database for each file
            UUID = str(uuid.uuid4().hex[:8])
            now = datetime.now()
            todayDate = now.strftime('%Y-%m-%d %H:%M:%S')
            # Uncomment and implement these according to your application's logic
            # invoice_upload.insert_file(filename, user_id, "1", UUID, project_name, company_code, todayDate)
            # invoice_upload.updated_by_UUID(UUID, '0')
            # sendtoprocess(user_id, company_code, filename, project_name, UUID, ocr_id, source_code, engine_id, doc_id)

        process_by = "Pradeep Yadav"

        # Return a success response
        return JsonResponse({"message": "Uploaded Successfully"}, safe=False)

    except Exception as e:
        print("Exception:", str(e))
        return JsonResponse({"status": "0", "message": "Error Something went wrong, Please try again", "uuid": "0"}, safe=False)


# #@api_view(["POST"])  
# def uploadfile(request):
#     ##print("$$$$$$$$$$$$",request.POST['config_id'])
#     if 'user_id' in request.session:
#         try:
#             #print("$$$$$$$$$$$$",request.POST['config_id'])
#             print(request)
#             user_id = str(request.session['user_id'])
#             company_code = get_company_code_from_session(request)
#             dictData = {}  
#             filename = request.FILES['file'].name
#             #fileindex = request.POST['file_index']
#             config_id = request.POST['config_id']
#             ocr_id = request.POST['ocr_id']
#             source_code = request.POST['source_code']
#             engine_id = request.POST['engine_id']
#             doc_id = request.POST['doc_id']
#             data = request.FILES['file']
            
#             print("****************************************************************************")

#             try:  
#                 tmp_file = os.path.join(settings.FILES_DIR,company_code,config_id, filename)  #os.path.join(os.getcwd() + "/upmapp/static/","DownloadFolder", filename)
#                 path = default_storage.save(tmp_file, ContentFile(data.read()))
                
#             except Exception as e:
#                 print("Exception In Code :",str(e))     

#             # Insert data into the database
#             UUID =  str(uuid.uuid4().hex[:8])
#             print(UUID)
#             now = datetime.now()
#             todayDate= now.strftime('%Y-%m-%d %H:%M:%S') 
#             invoice_upload.insert_file(filename,user_id,"1",UUID,config_id,company_code,todayDate)
#             sendtoprocess(user_id,company_code,filename,config_id,UUID,ocr_id,source_code,engine_id,doc_id)
#             process_by = request.user.first_name + " " + request.user.last_name
#             result =  {"message" : "Uploaded Successfully",'file_name':filename,'file_id':UUID,'process_by': process_by,'process_date':todayDate, 'config_name':config_id} 
#             return JsonResponse(result,safe=False)
#         except Exception as e:
#             print(str(e))
#             result =  {"status" : "0", "message" : "Error Some thing went wrong, Please try again","uuid" : "0" } 
#             return JsonResponse(result,safe=False)
#     else:
#         result =  {"status" : "0", "message" : "Login session has expired, Please login again","uuid" : "0" } 
#         return JsonResponse(result,safe=False)



def sendtoprocess(user_id,company_code,filename,config_uuid,invoice_uuid,ocr_id,source_code,engine_id,doc_id):
    if user_id :
        try:
            '''
            dictData = {}
            dictData = json.loads(request.data["file_info"])
            user_id=str(request.session['user_id'])
            company_code = str(request.session['company_code'])
            file_name = dictData['file_name']
            invoice_uuid = dictData['invoice_uid']
            config_uuid = dictData['config_uuid'] 
            '''        
            
            invoice_upload.updated_by_UUID(invoice_uuid,'9')
            data = {'file_name':filename, 'user_id':company_code, "config_id" : config_uuid, 'business_user':user_id,'ocr_id':ocr_id, 'engine_id':engine_id,'doc_id':doc_id}
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",data)

            headers = {
                    'Authorization': f'Bearer {settings.API_TOKEN}',  # Attach the Bearer token to the header
                }
            
            try:
                print("*********")
                response = requests.post(url = settings.API_LINK, headers=headers, data = data)
            except Exception as e:
                print("------------")
                invoice_upload.updated_by_UUID(invoice_uuid,'1')
                #logger.error(str(e)) 
             
            responseObj = response.json()
            #if responseObj["success"] == '0':
               #invoice_upload.updated_by_UUID(invoice_uuid,'4')
                
            #UUID =  str(uuid.uuid4().hex[:8])
            obj_processed = processed_items()
            result=obj_processed.save_idp_output(user_id,config_uuid,responseObj['static'],responseObj['dynamic'],invoice_uuid,invoice_uuid,company_code)        
            if result == "Miscellaneous Action found":
                ret_dict = {'success' : "0", 'message':'Miscellaneous Action found.' }
                invoice_upload.updated_by_UUID(invoice_uuid,'4')
            else: 
                # Update invoice status
                invoice_upload.updated_by_UUID(invoice_uuid,'2')
                ret_dict = {'success' : "1", 'message':'File processed successfully.' }
            
            return  HttpResponse(json.dumps(ret_dict))
        except Exception as e:
            print(str(e))
            #logger.error(str(e))
            invoice_upload.updated_by_UUID(invoice_uuid,'4') 
            ret_dict = {'success' : "0", 'message':'Something went wrong, Please connect with Admin' }
            return  HttpResponse(json.dumps(ret_dict))
    else:
        #logger.error(str(e))
        invoice_upload.updated_by_UUID(invoice_uuid,'4')
        ret_dict = {'success' : "0", 'message':'Something went wrong, Please connect with Admin' }
        return  HttpResponse(json.dumps(ret_dict))

 

def get_user_from_session(request): 
     return str(request.session['user_id'])

def get_company_code_from_session(request): 
     return str(request.session['company_code'])
