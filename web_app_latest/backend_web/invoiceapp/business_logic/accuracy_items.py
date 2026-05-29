
from datetime import datetime
import uuid
from invoiceapp.db_operations.databaseconnection import databaseconnection

class accuracy_items:

    def __init__(self):
        pass     
 
    def get_audited_static_data(self,user_id,fromDate, toDate,predicted_uuid,company_code): 
        query = "SELECT uuid, file_name ,po_number ,invoice_number ,account_number,tax_amount ,invoice_date ,net_amount ,shipping_amount,currency ,invoice_type  ,delivery_address ,tax ,s_1 ,s_2 ,s_3 ,s_4 ,s_5 ,s_6 ,s_7 ,s_8 ,s_9 ,s_10,s_11,s_12,s_13,s_14,s_15,s_16,s_17,s_18,s_19,s_20,s_21,s_22,s_23,s_24,s_25 "
        query = query + " from audited_data WITH (NOLOCK)  where uuid =  '" + predicted_uuid + "' and company_code = '" + company_code + "'  AND  CONVERT(varchar(10), cast(audited_datetime as date),101) between CONVERT(varchar(10),cast('" + str(fromDate) +"' as date) ,101) and CONVERT(varchar(10),cast('" + str(toDate) +"' as date), 101) "
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result
    
    def get_predicted_static_data(self,user_id,predicted_ids,company_code): 
        query = "SELECT predicted_uuid, file_name ,po_number ,invoice_number ,account_number,tax_amount ,invoice_date ,net_amount ,shipping_amount,currency ,invoice_type  ,delivery_address ,tax ,s_1 ,s_2 ,s_3 ,s_4 ,s_5 ,s_6 ,s_7 ,s_8 ,s_9 ,s_10,s_11,s_12,s_13,s_14,s_15,s_16,s_17,s_18,s_19,s_20,s_21,s_22,s_23,s_24,s_25 "
        query = query + " from predicted_data WITH (NOLOCK) where company_code = '" + company_code + "' and predicted_uuid in (" + predicted_ids + ")"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result
    
    def insert_accuracy(self,user_id,config_id,accuracy_percent,accuracy_date,file_uuid,company_code):
        query = "Insert into accuracy_info (user_id,file_uuid,predicted_uuid,config_uuid,accuracy_percent,accuracy_date,company_code) "
        query = query + " values('"+ user_id +"','"+ file_uuid +"','','"+ config_id +"','"+  str(accuracy_percent) +"','"+ str(accuracy_date) +"','"+ str(company_code) +"')"
        _db = databaseconnection()
        result = _db.execute_non_query(query) 
        return result
    
    def get_accuracy_detail(user_id,startdate,enddate,company_code):

        from_date= startdate 
        to_date= enddate
        query =  " select ui.file_name as file_name ,CEILING(accuracy_percent) as accuracy_percent,CONVERT(varchar(10),accuracy_date, 101) as accuracy_date from accuracy_info ai WITH (NOLOCK) inner join user_invoices ui WITH (NOLOCK) on ui.invoice_uid = ai.file_uuid"
         
        query += " where "
        if user_id != "" and user_id != "0" :
            query += " ai.company_code  = '" + company_code + "'" 
           
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result 

 
    

