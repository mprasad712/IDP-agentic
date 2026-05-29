import uuid
import shutil
import ast
import requests
import traceback
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


@api_view(["POST"])
def invoiceprocess(request):
    if 'user_id' in request.session:
        try:
            dictData = {}
            dictData = json.loads(request.data["file_info"])
            user_id=str(request.session['user_id'])
            company_code = str(request.session['company_code'])
            file_name = dictData['file_name']
            invoice_uuid = dictData['invoice_uid']
            config_uuid = dictData['config_uuid']         
            
            invoice_upload.updated_by_UUID(invoice_uuid,'9')
            data = {'file_name':file_name, 'user_id':company_code, "config_id" : config_uuid, 'business_user':user_id}
            headers = {
                    'Authorization': f'Bearer {settings.API_TOKEN}',  # Attach the Bearer token to the header
                    'Content-Type': 'application/json'   # You can modify headers depending on the API requirements
                }
            
            try:
                print("posting response=============================================")
                response = requests.post(url = settings.API_LINK, data = data, headers=headers)
            except Exception as e:
                traceback.print_exc()
                invoice_upload.updated_by_UUID(invoice_uuid,'1')
                #logger.error(str(e)) 
             
            responseObj = response.json()
            #if responseObj["success"] == '0':
               #invoice_upload.updated_by_UUID(invoice_uuid,'4')
                
            UUID =  str(uuid.uuid4().hex[:8])
            obj_processed = processed_items()
            result=obj_processed.save_idp_output(user_id,config_uuid,responseObj['static'],responseObj['dynamic'],UUID,invoice_uuid,company_code)        
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
