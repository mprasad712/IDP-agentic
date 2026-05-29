# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 14:15:46 2020

@author: Pradeep Yadav
"""
 
import datetime
import os
 
from collections import OrderedDict
from . accuracy_items import accuracy_items
from datetime import datetime, timedelta

def get_item_from_audit(itemIndex, Keyname,list_audit_dict):
    selected_item = list_audit_dict[itemIndex]
    result = selected_item.get(Keyname)
    return result


 
def calculate_accuracy(static_predicted_dict,static_audited_dict):
    
    total_incorrect_fields = 0.0
    zeroth_item = static_predicted_dict[0]
    fields_count = 0
    for key,value in zeroth_item.items():
        audited_value = get_item_from_audit(0,key,static_audited_dict)
        
        if audited_value == None and value == None:             
            pass
        else:
            if value != None:
                fields_count = fields_count + 1
    
    total_fields =  fields_count     
    row_index = 0
    
    for row in static_predicted_dict:
        if row_index == 0:
            
            for key, value in row.items():             
                audited_value = get_item_from_audit(row_index,key,static_audited_dict)
                
                if(audited_value == None):
                    pass                    
                else:
                    if (audited_value != value):
                        total_incorrect_fields += 1.0
            print(total_incorrect_fields)
            accuracy = ((total_fields - total_incorrect_fields)/total_fields)*100.0
             
            row_index = row_index + 1
        
    
    return accuracy

def get_ids_from_predicted(predicted_dict):
    UUID = ""
     
    for row in predicted_dict:
        for key, val in row.items():
            if key == "uuid" :
             UUID = UUID + ",'"+ val + "'"
    if(UUID != ""):
        UUID = UUID[1:]
    return UUID

def init_accuracy(user_id,config_id,file_uuid,start_date,end_date,predicted_uuid,company_code):
    try:
        
        obj_accuracy_items = accuracy_items()
        audited_data = obj_accuracy_items.get_audited_static_data(user_id,start_date,end_date,predicted_uuid,company_code)
        results = get_ids_from_predicted(audited_data)
        predicted_data = obj_accuracy_items.get_predicted_static_data(user_id,results,company_code)
    
        accuracy_percent = calculate_accuracy(predicted_data,audited_data)
        print(accuracy_percent)
        obj_accuracy_items.insert_accuracy(user_id,config_id,accuracy_percent,start_date,file_uuid,company_code)
        
    except Exception as e:
        raise
    



# D=9
# fromDate_datetime = datetime.now() - timedelta(days=D) 
# fromDate= fromDate_datetime.date()

# toDate_datetime = datetime.now()+ timedelta(days=1)
# toDate= toDate_datetime.date()
# get_data("5039","","file-1",fromDate,toDate)

        
