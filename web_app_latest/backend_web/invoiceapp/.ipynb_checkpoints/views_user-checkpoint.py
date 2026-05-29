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
from rest_framework import status
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
 

def profile(request): 
     if 'user_id' in request.session:
        user_id =  get_user_from_session(request)
        company_code = get_company_code_from_session(request)
        user_info = users.get_user_full_info(user_id)
        print(user_info)
        processed_items.free_invoice("1",user_id)
        config_list =  site_settings.get_configuration_list(user_id,company_code)
        print(config_list)
        if len(config_list) == 0:
            config_list =  site_settings.get_default_settings()
            
        result = {'user_info':user_info, "allowed_by_admin" : config_list, "status": status.HTTP_200_OK}
        print(result)
        return JsonResponse(result)
    # else:



 
def get_user_from_session(request): 
     return str(request.session['user_id'])

def get_company_code_from_session(request): 
     return str(request.session['company_code'])

