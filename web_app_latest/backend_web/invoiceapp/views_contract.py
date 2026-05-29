
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
 

@login_required
def contract_dashboard(request):
    _objUser = users.get_user_info(request.session["user_id"])
    #print("user info",_objUser) 
    dashboard_data = {} 
    request.session["user_profle_image"] = _objUser[0]["profile_img"]
    request.session["user_org_image"] = _objUser[0]["org_img"]
    request.session["is_local_admin"] = _objUser[0]["is_local_admin"] 
    request.session["company_code"] = _objUser[0]["company_code"]
    user_id = get_user_from_session(request) 
    request.session["user_code"] = user_id
    dashboard_data["master_stats"]= dashboard_items.get_master_stats()
    return render(request,'views/contract/contract_dashboard.html', { 'idp_data': "Dashboard","master_data": dashboard_data } )


#contract view
def contract_configuration(request):
    user_id = get_user_from_session(request)
    if users.user_type(user_id) == 1:
        return render(request,'views/contract/contract_layout.html')
    else:
         return render(request,'views/login.html')


def get_user_from_session(request): 
     return str(request.session['user_id'])

def get_company_code_from_session(request): 
     return str(request.session['company_code'])

