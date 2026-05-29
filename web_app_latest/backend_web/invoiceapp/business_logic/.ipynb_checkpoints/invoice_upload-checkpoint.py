from invoiceapp.db_operations.databaseconnection import databaseconnection
from datetime import datetime
from invoiceapp.business_logic.customfields import customfields
from datetime import datetime

class invoice_upload:   
    def __init__(self):
        pass     

    def file_uploaded_count(user_id,company_code):
        query = "Select Count(id) as recCount from user_invoices WITH (NOLOCK) where company_code = '" + company_code +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query)
        return result[0]["recCount"]


    def scanfile_uploaded_count(user_id,company_code):
        query = "Select Count(id) as recCount from user_scan_invoices WITH (NOLOCK) where company_code = '" + company_code +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query)
        return result[0]["recCount"]

    
    def get_config_uuid(file_id):
        query = "SELECT config_id as config_uuid FROM user_invoices WITH (NOLOCK) where invoice_uid = '" + str(file_id) +"'"  
        _db = databaseconnection()
        result = _db.execute_Query(query) 
         
        return result[0]["config_uuid"]


    def insert_file(file_name,user_id,status,invoice_uid,config_id,company_code,todayDate):  
        query = "Insert into user_invoices (original_file_name,file_name,user_id,updated_datetime,status,invoice_uid,config_id,run_by,company_code) values "
        query += "('" + file_name + "' ,'" + file_name + "' ,'" + user_id + "','" + todayDate + "','"+ status+"','"+ invoice_uid+"','"+ config_id+"','manual','"+ company_code+"')"
        _db = databaseconnection()
        result = _db.execute_non_query(query)        
        return result

    def delete_by_ID(file_id):
        query = "Delete from  user_invoices where invoice_uid = '" + file_id + "'"          
        _db = databaseconnection()
        _db.execute_non_query(query)        
        return ""
    
    def updated_by_UUID(invoice_uuid,status):
        query = "Update user_invoices set status = '"+status+"' where invoice_uid = '" + invoice_uuid + "'"          
        _db = databaseconnection()
         
        _db.execute_non_query(query)        
        return ""

    def get_all(user_id,company_code):
        query = "Select au.first_name as first_name, au.last_name as last_name , original_file_name,ui.id,file_name,convert(varchar, updated_datetime, 0) AS updated_datetime , "
        query = query + " status,invoice_uid, ui.config_id as config_uuid , fm.config_name from user_invoices ui WITH (NOLOCK) "
        query = query + " inner join form_fields_master fm WITH (NOLOCK) on fm.config_uuid = ui.config_id AND  fm.company_code = ui.company_code"
        query = query + " inner join auth_user au WITH (NOLOCK)  on au.id = ui.user_id  "
        query = query + " where  status in (1,4,9)  and ui.company_code = '" + company_code+"'"      
        _db = databaseconnection()
        print(query)
        result = _db.execute_Query(query)        
        return result

    def get_all_invoicelist(user_id):
        query = "Select original_file_name,ui.id,file_name,convert(varchar, updated_datetime, 0) AS updated_datetime ,status,invoice_uid, ui.config_id as config_uuid , fm.config_name from user_invoices ui WITH (NOLOCK) inner join form_fields_master fm WITH (NOLOCK) on fm.config_uuid = ui.config_id  where  ui.user_id = " + user_id         
        _db = databaseconnection()
        result = _db.execute_Query(query)        
        return result

    def insert_classifire(file_name,user_id,status,invoice_uid,company_code,class_name,keywords):  
                    
        now = datetime.now()
        todayDate= now.strftime('%Y-%m-%d %H:%M:%S')
        query = "Insert into user_classification_invoices (original_file_name,file_name,class_name,keywords,user_id,updated_datetime,status,invoice_uid,config_id,run_by,company_code) values "
        query += "('" + file_name + "' ,'" + file_name + "' ,'" + class_name + "','" + keywords + "','" + user_id + "','" + todayDate + "','"+ status+"','"+ invoice_uid+"','','" + user_id + "','"+ company_code+"')"
        _db = databaseconnection()
        result = _db.execute_non_query(query)        
        return result

    def fetch_class_name(company_code):
        query = "Select distinct(class_name) from  user_classification_invoices where company_code= '" + company_code + "' "         
        _db = databaseconnection()
        result = _db.execute_Query(query)        
        return result

    def get_document_detail(document_id):
        query = "select file_name,invoice_uid, company_code,invoice_data from user_scan_invoices where invoice_uid='" + document_id + "' "
        _db = databaseconnection()
        result = _db.execute_Query(query)        
        return result


    def get_translated_detail(document_id):
        query = "select file_name,invoice_uid, company_code,invoice_data  from user_translation_doc where invoice_uid='" + document_id + "' "
        _db = databaseconnection()
        print(query)
        result = _db.execute_Query(query)        
        return result



    def fetch_digitized_docs_byid(self, document_id ):
        document_id = self.conver_to_uid(document_id)
        query = "select document_id, user_id,run_by, company_code, document_name,digitized_document_name,renamed_filename, status, created_time\
                from "+self.digitize_doc+" where document_id=? "
        query_params = (document_id,)
        rows = self.fetch_rows(query, query_params)
        req_rows = [r for r in rows if r['status']==2]
        return req_rows

    def insert_scan_file(file_name,user_id,status,invoice_uid,company_code):  
                    
        now = datetime.now()
        todayDate= now.strftime('%Y-%m-%d %H:%M:%S')
        query = "Insert into user_scan_invoices (original_file_name,file_name,user_id,updated_datetime,status,invoice_uid,config_id,run_by,company_code) values "
        query += "('" + file_name + "' ,'" + file_name + "' ,'" + user_id + "','" + todayDate + "','"+ status+"','"+ invoice_uid+"','','" + user_id + "','"+ company_code+"')"
        _db = databaseconnection()
        result = _db.execute_non_query(query)        
        return result

    def insert_translate_file(file_name,user_id,status,invoice_uid,company_code):  
                    
        now = datetime.now()
        todayDate= now.strftime('%Y-%m-%d %H:%M:%S')
        query = "Insert into user_translation_doc (original_file_name,file_name,user_id,updated_datetime,status,invoice_uid,config_id,run_by,company_code) values "
        query += "('" + file_name + "' ,'" + file_name + "' ,'" + user_id + "','" + todayDate + "','"+ status+"','"+ invoice_uid+"','','" + user_id + "','"+ company_code+"')"
        _db = databaseconnection()
        result = _db.execute_non_query(query)        
        return result

    def update_scan_invoice_status(id,company_code,invoice_data):
        now = datetime.now()
        todayDate= now.strftime('%Y-%m-%d %H:%M:%S')
        query = "UPDATE user_scan_invoices SET updated_datetime='" + todayDate + "', status='2', invoice_data='" + invoice_data +"'  WHERE id='" + id + "' AND company_code='" + company_code + "'  "
        _db = databaseconnection()
        #print("Query",query)
        result = _db.execute_non_query(query)        
        return result


    def update_translation_status(id,company_code,invoice_data):
        now = datetime.now()
        todayDate= now.strftime('%Y-%m-%d %H:%M:%S')
        query = "UPDATE user_translation_doc SET updated_datetime='" + todayDate + "', status='2', invoice_data='" + invoice_data +"'  WHERE invoice_uid='" + id + "' AND company_code='" + company_code + "'  "
        print("@@@@@@@@@@@@@@@@@@@@@@",query)
        _db = databaseconnection()
        result = _db.execute_non_query(query)        
        return result

    def delete_scan_ID(file_id):
        query = "Delete from  user_scan_invoices where id = '" + file_id + "'"          
        _db = databaseconnection()
        _db.execute_non_query(query)        
        return ""

    def delete_translate_ID(file_id):
        query = "Delete from  user_translation_doc where id = '" + file_id + "'"          
        _db = databaseconnection()
        _db.execute_non_query(query)        
        return ""
        
    def get_all_scaninvoice(user_id,company_code):
        query = "Select au.first_name as first_name, au.last_name as last_name , original_file_name,ui.id,file_name,convert(varchar, updated_datetime, 0) AS updated_datetime , "
        query = query + " status,invoice_uid, ui.config_id as config_uuid,ui.company_code  from user_scan_invoices ui WITH (NOLOCK) "
        query = query + " inner join auth_user au WITH (NOLOCK)  on au.id = ui.user_id  "
        query = query + " where  status='1'  and ui.company_code = '" + company_code+"'"      
        _db = databaseconnection()
        result = _db.execute_Query(query)        
        return result

    def get_all_originalinvoice(user_id,company_code):
        query = "Select au.first_name as first_name, au.last_name as last_name , original_file_name,ui.id,file_name,convert(varchar, updated_datetime, 0) AS updated_datetime , "
        query = query + " status,invoice_uid, ui.config_id as config_uuid,ui.company_code  from user_translation_doc ui WITH (NOLOCK) "
        query = query + " inner join auth_user au WITH (NOLOCK)  on au.id = ui.user_id  "
        query = query + " where  status='1'  and ui.company_code = '" + company_code+"'"      
        _db = databaseconnection()
        #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",query)
        result = _db.execute_Query(query)        
        return result

    def get_all_digitize_invoice(user_id,company_code):
        query = "Select au.first_name as first_name, au.last_name as last_name , original_file_name,ui.id,file_name,convert(varchar, updated_datetime, 0) AS updated_datetime , "
        query = query + " status,invoice_uid, ui.config_id as config_uuid,ui.company_code  from user_scan_invoices ui WITH (NOLOCK) "
        query = query + " inner join auth_user au WITH (NOLOCK)  on au.id = ui.user_id  "
        query = query + " where  status='2'  and ui.company_code = '" + company_code+"'"      
        _db = databaseconnection()
        result = _db.execute_Query(query)        
        return result


    def translated_invoice(user_id,company_code):
        query = "Select au.first_name as first_name, au.last_name as last_name , original_file_name,ui.id,file_name,convert(varchar, updated_datetime, 0) AS updated_datetime , "
        query = query + " status,invoice_uid, ui.config_id as config_uuid,ui.company_code  from user_translation_doc ui WITH (NOLOCK) "
        query = query + " inner join auth_user au WITH (NOLOCK)  on au.id = ui.user_id  "
        query = query + " where  status='2'  and ui.company_code = '" + company_code+"'"      
        _db = databaseconnection()
        result = _db.execute_Query(query)        
        return result


     
