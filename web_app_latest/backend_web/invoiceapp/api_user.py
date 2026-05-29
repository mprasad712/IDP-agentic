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

from django.contrib.auth import logout as django_logout
from django.views.decorators.cache import cache_control 
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate
import calendar;
import time;


# Business Libraries
from invoiceapp.business_logic.site_settings import site_settings
from invoiceapp.business_logic.customfields import customfields
from invoiceapp.business_logic.processed_items import processed_items
  
from invoiceapp.business_logic.invoice_upload import invoice_upload
from invoiceapp.business_logic.users import users
from invoiceapp.business_logic.dashboard_items import dashboard_items
from invoiceapp.business_logic.deleted_invoice import deleted_invoice
from invoiceapp.business_logic.issue_report import issue_report

@api_view(["POST"])
def update_profile(request):
    user_id = get_user_from_session(request)
    dictData = {}    
    dictData = request.data
    print(dictData,"aaabbbccc")
    try:
        business_email  = dictData.get("business_email")
        print(business_email,"------------------")
        organization_name = dictData.get("organization_name")                                                                                                            
        primary_contact_number  = dictData.get("primary_contact_number")                                                                                                       
        secondary_contact_number = dictData.get("secondary_contact_number")                                                                                                      
        mailing_address = dictData.get("mailing_address")                                                                                                                 
        organization_size = dictData.get("organization_size")                                                                                                               
        about_organization = dictData.get("about_organization")

        schedule_interval = dictData.get("schedule_interval")
        schedule_time = dictData.get("schedule_time")
        file_shared_location = dictData.get("file_shared_location")
        
        result = users.update_user_profile(user_id,business_email,organization_name,primary_contact_number,secondary_contact_number,mailing_address,organization_size,about_organization,schedule_interval,schedule_time,file_shared_location)
        responsedict = {"status":"1","message" : "User setting update successfully."}
        return HttpResponse(json.dumps(responsedict))
    except Exception as e: 
        responsedict = {"status":'0',"message" : "Invalid information Please check entered details."}
        return HttpResponse(json.dumps(responsedict)) 

@api_view(["POST"])
def upload_organization_pic(request):
    if 'user_id' in request.session:
        try:
            #print("upload Organization LOGO")
            user_id = get_user_from_session(request)
            
            dictData = {}   
            data = request.FILES['file']
            filename = request.FILES['file'].name
            
            if not os.path.exists(settings.ORGANIZATION_LOGO_ROOT + "/"+ user_id):
                os.makedirs(settings.ORGANIZATION_LOGO_ROOT + "/"+ user_id)

            tmp_file = os.path.join(settings.ORGANIZATION_LOGO_ROOT,user_id, filename)  
            path = default_storage.save(tmp_file, ContentFile(data.read()))
 
            users.update_organization_pic(user_id,filename) 
            result =  {"success" : "1","file_name" : filename,"message" : "Organization Logo updated successfully.","user_id" : user_id } 
            request.session["user_profle_image"] =  filename
            return JsonResponse(result,safe=False)
        except Exception as e:
            
            result =  {"success" : "0","file_name" : filename ,"message" : "Something went wrong please try again.","user_id" : user_id} 
            return JsonResponse(result,safe=False)
    else:
        result =  {"success" : "0","file_name" : "" ,"message" : "You are not authorized to access.","user_id" : ""} 
        return JsonResponse(result,safe=False)


@api_view(["POST"])
def upload_profile_pic(request):
    try:
        user_id= get_user_from_session(request)
        dictData = {}
        
        data = request.FILES['file']
        filename = request.FILES['file'].name
        print(filename,"2222")
        
        if not os.path.exists(settings.PROFILE_DIR + "/"+ user_id):
            os.makedirs(settings.PROFILE_DIR + "/"+ user_id)
       
        tmp_file = os.path.join(settings.PROFILE_DIR,user_id, filename)  
        print("333")
        path = default_storage.save( os.path.join(settings.PROFILE_DIR,user_id, filename) , ContentFile(data.read()))
        print("444")

        # Update user profile pic
        
        users.update_profile_pic(user_id,filename) 
        result =  {"success" : "1","file_name" : filename,"message" : "Profile Pic updated successfully.","user_id" : user_id } 
        return JsonResponse(result,safe=False)
    except Exception as e:
        print(e)
        result =  {"success" : "0","file_name" : filename ,"message" : "Something went wrong please try again.","user_id" : user_id} 
        return JsonResponse(result,safe=False)
    


# @api_view(["POST"])
# def update_profile(request):
#     if 'user_id' in request.session:
#         user_id= get_user_from_session(request)
#         dictData = {}    
#         dictData = ast.literal_eval(request.data["userInfo"])
#         try:
#             business_email  = dictData["business_email"]
#             organization_name = dictData["organization_name"]                                                                                                               
#             primary_contact_number  = dictData["primary_contact_number"]                                                                                                         
#             secondary_contact_number = dictData["secondary_contact_number"]                                                                                                        
#             mailing_address = dictData["mailing_address"]                                                                                                                 
#             organization_size = dictData["organization_size"]                                                                                                               
#             about_organization = dictData["about_organization"]

#             schedule_interval = dictData["schedule_interval"]
#             schedule_time = dictData["schedule_time"]
#             file_shared_location = dictData["file_shared_location"]
            
#             result = users.update_user_profile(user_id,business_email,organization_name,primary_contact_number,secondary_contact_number,mailing_address,organization_size,about_organization,schedule_interval,schedule_time,file_shared_location)
#             responsedict = {"status":"1","message" : "User setting update successfully."}
#             return HttpResponse(json.dumps(responsedict))
#         except Exception as e: 
#             responsedict = {"status":'0',"message" : "Invalid information Please check entered details."}
#             return HttpResponse(json.dumps(responsedict)) 
#     else:
#         responsedict = {"status":'0',"message" : "You are not authorized to access."}
#         return HttpResponse(json.dumps(responsedict)) 


# @api_view(["POST"])
# def upload_profile_pic(request):
#     if 'user_id' in request.session:
#         filename = ""
#         user_id = get_user_from_session(request)
#         try:
             
#             dictData = {}   
#             data = request.FILES['file']
#             filename = request.FILES['file'].name
            
#             if not os.path.exists(settings.PROFILE_DIR + "/"+ user_id):
#                 os.makedirs(settings.PROFILE_DIR + "/"+ user_id)

#             tmp_file = os.path.join(settings.PROFILE_DIR,user_id, filename)  
#             path = default_storage.save(tmp_file, ContentFile(data.read()))

#             # Update user profile pic
            
#             users.update_profile_pic(user_id,filename) 
#             result =  {"success" : "1","file_name" : filename,"message" : "Profile Pic updated successfully.","user_id" : user_id } 
#             return JsonResponse(result,safe=False)
#         except Exception as e:
#             print(e)
#             result =  {"success" : "0","file_name" : filename ,"message" : "Something went wrong please try again.","user_id" : user_id} 
#             return JsonResponse(result,safe=False)
#     else:
#         result =  {"success" : "0","file_name" : "" ,"message" : "You are not authorized to access.","user_id" : ""} 
#         return JsonResponse(result,safe=False)

def get_user_from_session(request): 
     return str(request.session['user_id'])

def get_company_code_from_session(request): 
     return str(request.session['company_code'])