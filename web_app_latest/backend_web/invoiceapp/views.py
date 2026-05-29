
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
from invoiceapp.business_logic.site_settings import site_settings
from django.views.decorators.cache import cache_control
from rest_framework.response import Response

import os

# Create your views here.
def index(request):
    return render(request,'index.html')
    
@login_required
def config_list(request):
    print("aaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbb")
    print(request.session.items(),"%%%%%%44444444444%%%%%%%")
    # if 'user_id' in request.session:
    user_id = get_user_from_session(request)
    company_code = get_company_code_from_session(request)
    print(user_id, company_code, "+++++++++++++++")
    usr = users()
    data = usr.get_configuration_list(user_id,company_code)
    return JsonResponse(data, safe=False)
    # else:
    #     return render(request,'index.html')

def processed(request):
    user_id = get_user_from_session(request)
    company_code = get_company_code_from_session(request)
    print(request.session['user_id'],"********^^^^^^^^^^^^^^^^")
    print(user_id, company_code, "++++++++++++------s+++")
    processed_items.free_invoice("1",user_id)
    _objList= processed_items.get_all_standard_data(user_id,company_code)   
    return JsonResponse(_objList, safe=False)

def validated(request):
    user_id = get_user_from_session(request)
    company_code = get_company_code_from_session(request)
    processed_items.free_invoice("1",user_id)
    _objList= audited_items.get_all_standard_data(user_id,company_code)  
    print(_objList,"$$$$$$")
    return JsonResponse(_objList, safe=False)

def invoicedeleted(request):
    user_id = get_user_from_session(request)
    company_code = get_company_code_from_session(request)
    processed_items.free_invoice("1",user_id)
    result = deleted_invoice.get_all_deleted(user_id,company_code) 
    return JsonResponse(result, safe=False)

def stpsupplier(request):  
    company_code = get_company_code_from_session(request)
    supplier_info = users.get_supplier(company_code)
    return JsonResponse(supplier_info, safe=False)

def processlog(request):         
    company_code = get_company_code_from_session(request)
    log_info = users.get_process_log(company_code)
    return JsonResponse(log_info, safe=False)
    
@login_required
def get_dashboard_data(request):
    dashboard = dashboard_items()
    print(request.session.items(),"%%%%%%%%%%%%%")
    company_code = get_company_code_from_session(request)
    data = {
        'file_upload_count': dashboard.get_file_upload_count(company_code),
        'processed_count': dashboard.get_processed_count(company_code),
        'audited_count': dashboard.get_audited_count(company_code),
        'digitized_count': dashboard.get_digitized_count(company_code),
        'classifire_count': dashboard.get_classifire_count(company_code),
        'failed_by_idp_count': dashboard.get_failed_by_idp_count(company_code),
        'register_user_count': dashboard.get_register_user(company_code),
        'active_supplier_count': dashboard.active_supplier(company_code),
        # Add more fields if needed
    }
    return JsonResponse(data)

def view_configuration(request):
    user_id = get_user_from_session(request)
    company_code = get_company_code_from_session(request)
    objcustom  = customfields()
    config_list = objcustom.get_configurations_List(user_id,company_code)
    dict_config = []
    for config in config_list:
        fieldsConfiguration = objcustom.get_custom_fields_by_uuid(config["config_uuid"],user_id,company_code)
        dict_config.append({"config_uuid" : config["config_uuid"], "config_name" : config["config_name"] ,"config_data" : fieldsConfiguration})
    return JsonResponse(dict_config, safe=False)
    
def get_dashboard_data_weekly(request):
    if 'user_id' in request.session:
        company_code = get_company_code_from_session(request)
    dashboard = dashboard_items()  
    data = {
        'file_upload_count_weekly': dashboard.get_file_upload_count_for_week(company_code),
        'file_processed_count_weekly': dashboard.get_file_processed_count_for_week(company_code),
        'file_audited_count_weekly': dashboard.get_file_audited_count_for_week(company_code),
    }
    return JsonResponse(data)

def userlist(request):   
    company_code = get_company_code_from_session(request)
    user_info = users.get_user_list(company_code)
    print(user_info)
    return JsonResponse(user_info, safe=False)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def login(request):
    return render(request,'views/login.html')

def terms_and_condition(request):
    return render(request,'views/terms_and_condition.html')

@login_required
def create_classifier(request):
    if 'user_id' in request.session:
        company_code = get_company_code_from_session(request)
        class_list = invoice_upload.fetch_class_name(company_code)
        return render(request,'views/create_classifier.html', { "class_list": class_list })
    else:
        return render(request,'views/login.html')



    

def audit_detail(request,pk):
    return render(request,'views/invoice_audit_detail.html')

     
def download(request):
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        objcustom  = customfields()
        config_list = objcustom.get_configurations_List(user_id,company_code)
        processed_items.free_invoice("1",user_id)     
        return render(request,'views/download.html',{'config_list':config_list }) 
    else:
        return render(request,'index.html')

def audit(request,pk):
    botdata = dashboard_items.get_botdata(pk)
    company_code = get_company_code_from_session(request)
    return render(request,'views/audit_document.html',{"botdata":botdata, 'company_code':company_code})

def define_layout(request):
    user_id = get_user_from_session(request)
    if users.user_type(user_id) == 1:
        return render(request,'views/define_layout.html')
    else:
         return render(request,'index.html')

def register(request):
    return render(request,'views/register.html', { 'WEB_API_LINK':settings.WEB_API_LINK } )

# def view_configuration(request):
#     if 'user_id' in request.session:
       
#         user_id = get_user_from_session(request)
#         company_code = get_company_code_from_session(request)
        
#         objcustom  = customfields()
#         config_list = objcustom.get_configurations_List(user_id,company_code)
#         dict_config = []
#         print(config_list)
#         for config in config_list:
            
#             fieldsConfiguration = objcustom.get_custom_fields_by_uuid(config["config_uuid"],user_id,company_code)
#             dict_config.append({"config_uuid" : config["config_uuid"], "config_name" : config["config_name"] ,"config_data" : fieldsConfiguration})
        
#         return render(request,'views/view_configuration.html',{'config_list':dict_config })
#     else:
#         return render(request,'views/login.html') 

def upload_invoice(request):
    if 'user_id' in request.session:        
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        count_file = invoice_upload.file_uploaded_count(user_id,company_code)
        config_list =  site_settings.get_configuration_list(user_id,company_code)
        
        #processed_items.free_invoice("1",user_id)
        if len(config_list) == 0:
            config_list =  site_settings.get_default_settings()
         
        allow_to_upload = 0
        for field in config_list:
            if field["setting_name"] =="max_file_upload":
                allow_to_upload = field["setting_value"]

        remaining_toupload = int(allow_to_upload) - int(count_file) 
        # get configurations name
        objcustom  = customfields()
        config_list = objcustom.get_configurations_List(user_id,company_code)
        return render(request,'views/upload_invoice.html',{'allow_to_upload':allow_to_upload,'count_file':count_file, 'remaining_toupload' : remaining_toupload , "config_list" : config_list })
    else:
        return render(request,'views/login.html')


def runidp(request):
   
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        _objList= invoice_upload.get_all(user_id,company_code)     
        #processed_items.free_invoice("1",user_id)
        return render(request,'views/runidp.html',{'user_invoices':_objList })
    else:
        return render(request,'views/login.html')
        
@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def login(request):
    return render(request,'views/login.html', {'WEB_API_LINK':settings.WEB_API_LINK } )

@csrf_exempt
def logout(request): 
    if 'user_id' in request.session:
        user_id = get_user_from_session(request)
        processed_items.free_invoice("1",user_id)
        # del request.session['user_profle_image']
        del request.session['user_id']
        del request.session['first_name']
        del request.session['last_name']
        del request.session['email']
        del request.session['company_code']
        # del request.session['user_org_image']
        # del request.session['user_code']

    django_logout(request)
    #print("Logout Redirect")
    return HttpResponseRedirect('/login/')


@login_required
@api_view(["POST"])
def change_password(request):
    print(f"Request Data: {json.dumps(request.data)}")
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.data)
        print("aaaaaaaaaaa")
    
        if form.is_valid():
            print("ccccccccccccccccc")
            user = form.save()
            update_session_auth_hash(request, user)  # Important! 
            return Response({'message': 'Your account password has been updated successfully!'}, status=200)
        else:
            return Response({'message': 'Please enter valid details.'}, status=400)
    return Response({'message': 'Method not allowed.'}, status=405)


@login_required
@api_view(["POST"])
def download_multiple_audit(request):
    
    if 'user_id' in request.session:
        
        user_id= str(request.session['user_id'])
        data = request.data
        config_uuid = data["layout"]
        print(config_uuid,"***")
        from_date = data["from_date"]
        to_date =data["to_date"]
        company_code = get_company_code_from_session(request)
        action_report_for = data["report_for"]

        obj_data = audited_itemdetails() 
        excelData_df = obj_data.Excel_Data_Templatewise(user_id,config_uuid,from_date,to_date,action_report_for,company_code)
        print("aaaa")
        excel_path= settings.EXCEL_EXPORT_ROOT+'report.csv'
        print(excel_path,"###$$$")
        print("vbbb")
        try:
            excelData_df.to_csv(excel_path)
        except Exception as e:
            print(e)
        print("cccc")
         
        f = open(excel_path , 'r')

        if action_report_for == 'predict_report':
            action_report_for ='processed_report'

        if action_report_for == 'user_invoice_report':
            action_report_for ='uploaded_data_report'

        custom_file_name= action_report_for+"_"+from_date.replace('/','_')+"-to-"+to_date.replace('/','_')+".csv"
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{custom_file_name}"'

        print(custom_file_name)
        return response
    else:
        return render(request,'views/login.html')


# 
def get_user_from_session(request): 
     print("user data", request.session['user_id'])
     return str(request.session['user_id'])

def get_company_code_from_session(request):
     #print("user data", request.session['company_code']) 
     return str(request.session['company_code'])


def download_audit_excel(request):
    if 'user_id' in request.session:
        user_id= str(request.session['user_id'])
        predicted_uuid = request.POST.get("predicted_uuid")
        company_code = get_company_code_from_session(request)
        obj_data = audited_itemdetails()
        
        excelData_df = obj_data.Excel_Data(user_id,predicted_uuid,"","",company_code)
        #print(excelData_df)
        #print("File Found")
        excel_path=  settings.EXCEL_EXPORT_ROOT+'report.xlsx'
        excelData_df.to_excel(excel_path)
         
        f = open(excel_path , 'rb')
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=auditReport.xlsx'
        return response 
     
@login_required
def audit_detail(request,pk):
    if 'user_id' in request.session:
        return render(request,'views/audit_detail.html',{"uuid" : str(pk)})
    else:
        return render(request,'views/login.html')



@api_view(["POST"])
def dashboard_stats(request,company_code):
    print("1111111111111111111111111")
    
    # if 'user_id' in request.session:
    try:
        dashboard_data = {}
        # user_id = get_user_from_session(request)
        # company_code = get_company_code_from_session(request)
        print("company_code",company_code)
        # register_user = dashboard_items.get_register_user(company_code)
        # active_supplier = dashboard_items.active_supplier(company_code)    

        file_upload_count = dashboard_items.get_file_upload_count(company_code)
        
        processed_count = dashboard_items.get_processed_count(company_code)
        audited_count = dashboard_items.get_audited_count(company_code)
        
        failed_by_idp_count = dashboard_items.get_failed_by_idp_count(company_code)
        digitized_count = dashboard_items.get_digitized_count(company_code)
        classifire_count = dashboard_items.get_classifire_count(company_code)
        
        # last_login = dashboard_items.last_login(user_id)
        
        # last_process = dashboard_items.last_process(company_code)
        # print("hello",last_process )
        
        # dashboard_data["register_user"] = register_user
        # dashboard_data["active_supplier"] = active_supplier
        dashboard_data["file_upload_count"] = file_upload_count
        dashboard_data["processed_count"] = processed_count
        dashboard_data["audited_count"] = audited_count
        dashboard_data["digitized_count"] = digitized_count
        dashboard_data["classifire_count"] = classifire_count
        dashboard_data["last_login"] = last_login
        dashboard_data["failed_by_idp_count"] = failed_by_idp_count
        
        if last_process:
            dashboard_data["last_process"] = last_process
        else:
            dashboard_data["last_process"] = "N/A"    
        dashboard_data["master_stats"]=json.dumps(dashboard_items.get_master_stats())
        ret_dict = {'dashboard_data': dashboard_data }
        return  HttpResponse(json.dumps(ret_dict))
    except Exception as e:
        print(e)
        ret_dict = {'dashboard_data': {} }
        return  HttpResponse(json.dumps(ret_dict))
    # else:
    #     ret_dict = {'message':'You are not authorized to access.' }
    #     return  HttpResponse(json.dumps(ret_dict))
        
        
        

        
def create_business_logic(request):
    user_id = get_user_from_session(request)
    if users.user_type(user_id) == 1:
        if 'user_id' in request.session:
            user_id = get_user_from_session(request)
            company_code = get_company_code_from_session(request)
            objcustom  = customfields()
            config_list = objcustom.get_configurations_List(user_id,company_code)
            return render(request,'views/create_business_logic.html',{'config_list' : config_list})
        else:
            return render(request,'views/login.html')
    else:
            return render(request,'views/login.html')


@api_view(["POST"])
def getbusinessrule_fields(request):
    if 'user_id' in request.session:
        company_code = get_company_code_from_session(request)
        dictData = {}    
        dictData = ast.literal_eval(request.data["bs_info"])
        user_id =  str(request.session['user_id'])
        configuration_uuid = dictData["config_uuid"]
        field_data_type = dictData["field_data_type"]
        
        objcustom  = customfields() 
        fieldsConfiguration = customfields.get_standard_fields_by_uuid(configuration_uuid,user_id,field_data_type,company_code)
        return JsonResponse(fieldsConfiguration,safe=False)
    else:
        result = {"message" : "You are not authorized to access","file_id" : file_id}              
        return JsonResponse(result,safe=False)

        
        
# def userlist(request):
#     user_id = get_user_from_session(request)
#     if users.user_type(user_id) == 1:
#         if 'user_id' in request.session:
#             company_code = get_company_code_from_session(request)                
#             user_info = users.get_user_list(company_code)
#             return render(request,'views/userlist.html',{'user_data':user_info })
#         else:
#             return render(request,'views/login.html')
#     else:
#          return render(request,'views/login.html')

 
@api_view(["POST"])
def getuserInfo(request):
    user_id = get_user_from_session(request)
    if users.user_type(user_id) == 1:
        if 'user_id' in request.session:
            try:
                dictData = {}    
                dictData = ast.literal_eval(request.data["userInfo"])
                
                user_id = dictData["Id"]  
                user_detail = users.get_user_info(user_id)     
                print(user_detail)
                result = {"user_detail" : user_detail,"status" : "1", "message" : ""}
                return  JsonResponse(result,safe=False)
            except Exception as e:
                print(str(e))
                result = {"user_detail" :{},"status" : "0", "message" : "Please try again."}
                return  JsonResponse(result,safe=False)

        else:
            result = {"user_detail" : {}, "status": "0","message" : "You are not authorized to access, Please login again."}
            return  JsonResponse(result,safe=False)
        
        
def updateuser(request):
    user_id = get_user_from_session(request)
    if users.user_type(user_id) == 1:     
        username = ''
        first_name = ''
        last_name = ''
        email = ''
        is_superuser = '' 
        is_active =''
        if request.POST:         
            userid = request.POST['userid']
            username = request.POST['username']
            first_name = request.POST['first_name']
            last_name= request.POST['last_name']
            email = request.POST['email']
            is_staff = request.POST['is_superuser']
             
            is_local_admin = is_staff
            
            is_active = request.POST['is_active']
            query = "UPDATE  auth_user SET  first_name='" +first_name+ "',last_name='" +last_name+ "',email='" +email+ "',is_local_admin='" + str(is_local_admin)+ "',is_active='" +is_active+ "' WHERE id='" +userid+ "' "  
             
            ret_dict=users.update_user_data(query)
            return HttpResponseRedirect('/userlist',{'status':'user updated successfully.'});  
        else:
            return render(request,'views/userlist.html', {'error':'Please check entered data, which is incorrect.'})
            
@api_view(["POST"])
def delete_field_config(request):
    print("@@@@@@@@@@@@@@@@@@@@@@")
    user_id = get_user_from_session(request)
    if users.user_type(user_id) == 1:
        if 'user_id' in request.session:
            try:
                user_id = get_user_from_session(request)
                dictData = {}    
                dictData = ast.literal_eval(request.data["field_info"])
                configuration_uuid = dictData["config_uuid"] 
                 
                objcustom  = customfields()
                #objcustom.delete_config(user_id,configuration_uuid)
                 
                if os.path.exists(settings.ACTIVE_LEARNING_ROOT + str(user_id) + "/" + str(configuration_uuid)):
                    shutil.rmtree(settings.ACTIVE_LEARNING_ROOT + str(user_id) + "/" + str(configuration_uuid))
                print("output path", settings.SOLUTION_OUTPUT_DATA + str(user_id) + "/" + str(configuration_uuid))
                if os.path.exists(settings.SOLUTION_OUTPUT_DATA + str(user_id) + "/" + str(configuration_uuid)):
                    shutil.rmtree(settings.SOLUTION_OUTPUT_DATA + str(user_id) + "/" + str(configuration_uuid))
                
                if os.path.exists(settings.INVOICE_DATA_ROOT + str(user_id) + "/" + str(configuration_uuid)):
                    shutil.rmtree(settings.INVOICE_DATA_ROOT +  str(user_id) + "/" + str(configuration_uuid))
                 

                result = {"status":"1","message":"Field configuration deleted successfully."}
                return JsonResponse(result,safe=False)
            except Exception as e:
                print(e)
                result = {"status":"0","message":"Error Please try again."}
                return JsonResponse(result,safe=False)
        else:
            result = {"status":"0","message":"You are not authorized to access."}
            return JsonResponse(result,safe=False)            
    else:
        result = {"status":"0","message":"You are not authorized to access."}
        return JsonResponse(result,safe=False)            
            

def feedback(request):
    return render(request,'views/feedback.html')
    


@api_view(["POST"])
def feedbacksubmit(request):
    dictData = {}    
    dictData = ast.literal_eval(request.data["userInfo"])
    if 'user_id' in request.session:
        if dictData["feedback"]:
            user_id =  str(get_user_from_session(request))
            rate = dictData["feedback"]
            feedback = dictData["message"]
            
            suc_feedback = users.insert_feedback(user_id,rate,feedback)

            result = {}   
            result["status"] = "1"
            result["message"] = "Feedback sent successfully."
            return  JsonResponse(result,safe=False)
            
        else:
            result = {}  
            result["status"] = "0"
            result["message"] = "Something went worng please try again."             
            return JsonResponse(result,safe=False)
    else:
        result = {}  
        result["id"] = id
        result["status"] = "0"
        result["message"] = "You are not authorized to access , please login again."             
        return JsonResponse(result,safe=False) 
        
        
@api_view(["POST"])        
def takeatour(request):
    user_id = get_user_from_session(request)   
    if user_id:
        dictData = {}    
        dictData = ast.literal_eval(request.data["field_info"])
                
        atour = dictData["atour"]         
        query = "UPDATE  auth_user SET  takeatour=' "+ atour +"' WHERE id='" +user_id+ "' "   
        ret_dict=users.update_user_data(query)
        result = {"status" : "1","message" : "Take a tour action perform successfully."}
        return JsonResponse(result,safe=False)  
    else:
        return render(request,'views/userlist.html', {'error':'Please check entered data, which is incorrect.'})           
        
def user_authentication(request,pk):
    return render(request,'views/user_authentication.html',{"uuid" : str(pk)})

 
@api_view(["POST"])
def api_activate_user(request):
    dictData = {}    
    dictData = ast.literal_eval(request.data["field_info"])
    auth_code = dictData["auth_code"]
    auth_pin = dictData["auth_pin"]
    try:
        if(users.is_admin_authenticate_user(auth_code,auth_pin) == True):
            result = {"status":"1","Message" : "User activated successfully."}
            return JsonResponse(result,safe=False)
        else:
            result = {"status":"0","Message" : "Authentication Pin is not valid."}
            return JsonResponse(result,safe=False)

         
    except Exception as e:
        print(e)
        result =  {"success" : "0","file_name" : "" ,"message" : "OOPS!! Something went wrong please try again."} 
        return JsonResponse(result,safe=False)
 
        
        

# def stpsupplier(request):
#     user_id = get_user_from_session(request)
#     company_code = get_company_code_from_session(request)
#     objcustom  = customfields()
#     config_list = objcustom.get_configurations_List(user_id,company_code)
#     return render(request,'views/add_suppliers.html', {"config_list" : config_list })


def stprules(request):
    user_id = get_user_from_session(request)
    company_code = get_company_code_from_session(request)
    objcustom  = customfields()
    config_list = objcustom.get_configurations_List(user_id,company_code)
    return render(request,'views/supplier_rules.html', {"config_list" : config_list })


# def processlog(request):
#     user_id = get_user_from_session(request)
#     if users.user_type(user_id) == 1:
#         if 'user_id' in request.session:
#             company_code = get_company_code_from_session(request)                
#             log_info = users.get_process_log(company_code)

#             return render(request,'views/process_log.html',{'log_info':log_info })
#         else:
#             return render(request,'views/login.html')
#     else:
#          return render(request,'views/login.html')


# def stpsupplier(request):
#     user_id = get_user_from_session(request)
#     if users.user_type(user_id) == 1:
#         if 'user_id' in request.session:
#             company_code = get_company_code_from_session(request)                
#             supplier_info = users.get_supplier(company_code)

#             return render(request,'views/stpsupplier.html',{'supplier_info':supplier_info })
#         else:
#             return render(request,'views/login.html')
#     else:
#          return render(request,'views/login.html')   



def rclassification(request):
    return render(request,'views/rice_classification.html', { 'WEB_API_LINK':settings.WEB_API_LINK } )               


def vauth(request):
    return render(request, 'views/voice_identifier.html', { 'WEB_API_LINK':settings.WEB_API_LINK }) 


def vauthaccount(request):
    return render(request, 'views/register_voice.html') 

@login_required
def session_data(request):
    # Use .get() with a default value to avoid KeyError
    user_id = request.session.get("user_id", None)
    first_name = request.session.get("first_name", "")
    first_letter = request.session.get("first_letter", "")
    last_name = request.session.get("last_name", "")
    last_letter = request.session.get("last_letter", "")
    email = request.session.get("email", "")
    web_api_link = request.session.get("WEB_API_LINK", "")
    prod_mode = request.session.get("prod_mode", False)
    company_code = request.session.get("company_code", "")

    # Make sure to return meaningful JSON data
    response_data = {
        "user_id": user_id,
        "first_name": first_name,
        "first_letter": first_letter,
        "last_name": last_name,
        "last_letter": last_letter,
        "email": email,
        "WEB_API_LINK": web_api_link,
        "prod_mode": prod_mode,
        "company_code": company_code,
    }

    return JsonResponse(response_data)



    
