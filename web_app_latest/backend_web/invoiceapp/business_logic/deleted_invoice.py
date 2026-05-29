from invoiceapp.db_operations.databaseconnection import databaseconnection
from datetime import datetime

from invoiceapp.business_logic.site_settings import site_settings
import uuid

class deleted_invoice:   
    def __init__(self):
        pass     

     
    def get_all_deleted(user_id,company_code):
        query = ("SELECT predicted_id,user_id,file_name, deleted_datetime, ISNULL(first_name,'') AS first_name,ISNULL(last_name,'') AS last_name "
        "FROM deleted_data pd WITH (NOLOCK) " 
        "left join auth_user au WITH (NOLOCK) on pd.deleted_by= au.id  where pd.company_code  = '"+ company_code +"'  ORDER BY pd.file_name "
        )
        print(query)
        _db = databaseconnection()
        result = _db.execute_Query(query)
        return result
    


    def invoice_delete(uid,predicted_uuid):
        _db = databaseconnection()

        query = "INSERT INTO deleted_data(user_id,file_name,po_number,invoice_number,account_number,tax_amount,invoice_date,net_amount,shipping_amount,currency,invoice_type,delivery_address,tax,s_1,s_2,s_3,s_4,s_5,s_6,s_7,s_8,s_9,s_10,s_11,s_12,s_13,s_14,s_15,s_16,s_17,s_18,s_19,s_20,s_21,s_22,s_23,s_24,s_25,created_datetime,predicted_status,predicted_by,UUID,vendor_name,company_name,config_uuid,predicted_uuid,row_amount,total_amount,invoice_address,conf_score,conf_file_name,conf_invoice_date,conf_currency,conf_s_3,conf_company_name,conf_total_amount,conf_account_number,conf_delivery_address,conf_s_2,conf_shipping_amount,conf_s_1,conf_invoice_address,conf_invoice_number,conf_s_4,conf_s_5,conf_s_6,conf_s_7,conf_s_8,conf_s_9,conf_s_10,conf_s_11,conf_s_12,conf_s_13,conf_s_14,conf_s_15,conf_s_16,conf_s_17,conf_s_18,conf_s_19,conf_s_20,conf_s_21,conf_s_22,conf_s_23,conf_s_24,conf_s_25,conf_tax_amount,conf_po_number,conf_net_amount,conf_invoice_type,conf_tax,conf_vendor_name,file_uuid,tax_2,tax_1,conf_tax_1,conf_tax_2,original_file_name,company_code) SELECT  user_id,file_name,po_number,invoice_number,account_number,tax_amount,invoice_date,net_amount,shipping_amount,currency,invoice_type,delivery_address,tax,s_1,s_2,s_3,s_4,s_5,s_6,s_7,s_8,s_9,s_10,s_11,s_12,s_13,s_14,s_15,s_16,s_17,s_18,s_19,s_20,s_21,s_22,s_23,s_24,s_25,created_datetime,predicted_status,predicted_by,UUID,vendor_name,company_name,config_uuid,predicted_uuid,row_amount,total_amount,invoice_address,conf_score,conf_file_name,conf_invoice_date,conf_currency,conf_s_3,conf_company_name,conf_total_amount,conf_account_number,conf_delivery_address,conf_s_2,conf_shipping_amount,conf_s_1,conf_invoice_address,conf_invoice_number,conf_s_4,conf_s_5,conf_s_6,conf_s_7,conf_s_8,conf_s_9,conf_s_10,conf_s_11,conf_s_12,conf_s_13,conf_s_14,conf_s_15,conf_s_16,conf_s_17,conf_s_18,conf_s_19,conf_s_20,conf_s_21,conf_s_22,conf_s_23,conf_s_24,conf_s_25,conf_tax_amount,conf_po_number,conf_net_amount,conf_invoice_type,conf_tax,conf_vendor_name,file_uuid,tax_2,tax_1,conf_tax_1,conf_tax_2,original_file_name,company_code  FROM  predicted_data WHERE predicted_uuid = '"+str(predicted_uuid)+"'"
         
        _db.execute_non_query(query)
        
        now = datetime.now()
        todayDate= now.strftime('%Y-%m-%d %H:%M:%S')

        update_query ="UPDATE deleted_data SET deleted_by='"+str(uid)+"', deleted_datetime='"+todayDate+"' WHERE predicted_uuid = '"+str(predicted_uuid)+"'"
        _db.execute_non_query(update_query)

        query = "INSERT INTO deleted_table_data(predicted_id,line_no,order_number,unit,quantity,description,t_1,t_2,t_3,t_4,t_5,t_6,t_7,t_8,t_9,t_10,t_11,t_12,t_13,t_14,t_15,t_16,t_17,t_18,t_19,t_20,t_21,t_22,t_23,t_24,t_25,created_datetime,predicted_table_status,user_id,UUID,predicted_uuid,unit_price,total_amount,invoice_address,config_uuid,amount) SELECT predicted_id,line_no,order_number,unit,quantity,description,t_1,t_2,t_3,t_4,t_5,t_6,t_7,t_8,t_9,t_10,t_11,t_12,t_13,t_14,t_15,t_16,t_17,t_18,t_19,t_20,t_21,t_22,t_23,t_24,t_25,created_datetime,predicted_table_status,user_id,UUID,predicted_uuid,unit_price,total_amount,invoice_address,config_uuid,amount FROM  predicted_table_data WHERE predicted_uuid = '"+str(predicted_uuid)+"'"
        _db.execute_non_query(query)
        
        query = "DELETE FROM predicted_data WHERE predicted_uuid = '"+str(predicted_uuid)+"'"
        _db.execute_non_query(query)
        
        query = "DELETE FROM predicted_table_data WHERE predicted_uuid = '"+str(predicted_uuid)+"' "
        _db.execute_non_query(query)

        query = "DELETE FROM audited_table_data WHERE uuid = '"+str(predicted_uuid)+"'"
        _db.execute_non_query(query)
        
        query = "DELETE FROM audited_table_data WHERE uuid = '"+str(predicted_uuid)+"' "
        _db.execute_non_query(query)
         
        return ''
    