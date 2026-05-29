from invoiceapp.db_operations.databaseconnection import databaseconnection
from datetime import datetime
from invoiceapp.business_logic.customfields import customfields
from django.contrib.auth.models import User
from datetime import datetime, timedelta
#from bson import json_util
import json


class dashboard_items:   
    def __init__(self):
        pass

    ##special case for react graph##
    def get_file_upload_count_for_week(self, company_code):
        # Calculate the start date as today's date
        start_date = datetime.now()
        
        # Calculate the end date as 7 days before the start date
        end_date = start_date - timedelta(days=6)
        
        # Adjust start_date to include the full day by setting time to 23:59:59
        start_date = start_date.replace(hour=23, minute=59, second=59)
        
        # Format dates to string for the query
        start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # SQL query to get file count grouped by date for the specified week
        query = f"""
            SELECT CONVERT(varchar, updated_datetime, 23) as upload_date, COUNT(1) as recCount
            FROM user_invoices WITH (NOLOCK)
            WHERE company_code = '{str(company_code)}'
            AND updated_datetime BETWEEN '{end_date_str}' AND '{start_date_str}'
            GROUP BY CONVERT(varchar, updated_datetime, 23)
            ORDER BY upload_date
        """
        
        _db = databaseconnection()
        results = _db.execute_Query(query)
        print(results,"@@E####")
        # Convert results to a dictionary with dates as keys
        datewise_counts = {result['upload_date']: result['recCount'] for result in results}
        
        # Ensure all 7 days are represented, fill missing days with 0
        current_date = end_date
        while current_date <= start_date:
            current_date_str = current_date.strftime('%Y-%m-%d')
            if current_date_str not in datewise_counts:
                datewise_counts[current_date_str] = 0
            current_date += timedelta(days=1)
        return datewise_counts


    def get_file_processed_count_for_week(self, company_code):
        start_date = datetime.now()
        # Calculate the start date as today's date and adjust to end of the day
        start_date = datetime.now().replace(hour=23, minute=59, second=59)
        
        # Calculate the end date as 6 days before the start date
        end_date = start_date - timedelta(days=6)
        
        # Format dates to string for the query
        start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # SQL query to get file count grouped by date for the specified week
        query = f"""

            SELECT CONVERT(varchar(10), created_datetime, 120) as upload_date, COUNT(1) as recCount
FROM predicted_data WITH (NOLOCK)
WHERE predicted_status in ('1','2')
AND company_code = '{str(company_code)}'
AND created_datetime BETWEEN '{end_date_str}' AND '{start_date_str}'
GROUP BY CONVERT(varchar(10), created_datetime, 120)
ORDER BY upload_date;



        """
        
        _db = databaseconnection()
        results = _db.execute_Query(query)
        print(results,"===")
        
        # Convert results to a dictionary with dates as keys
        datewise_counts = {}
        
        for result in results:
            # Ensure the date is used correctly as a key
            date_str = result['upload_date'][:10]  # Extract only the date part
            datewise_counts[date_str] = result['recCount']
        
        # Ensure all 7 days are represented, fill missing days with 0
        current_date = end_date
        while current_date <= start_date:
            current_date_str = current_date.strftime('%Y-%m-%d')
            if current_date_str not in datewise_counts:
                datewise_counts[current_date_str] = 0
            current_date += timedelta(days=1)
        
        return datewise_counts


    def get_file_audited_count_for_week(self, company_code):
        # Calculate the start date as today's date and adjust to the end of the day
        start_date = datetime.now().replace(hour=23, minute=59, second=59)
        
        # Calculate the end date as 6 days before the start date
        end_date = start_date - timedelta(days=6)
        
        # Format dates to string for the query
        start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # SQL query to get file count grouped by date for the specified week
        query = f"""
            SELECT CONVERT(varchar, audited_datetime, 23) as upload_date, COUNT(1) as recCount
            FROM audited_data WITH (NOLOCK)
            WHERE company_code = '{str(company_code)}'
            AND audited_datetime BETWEEN '{end_date_str}' AND '{start_date_str}'
            GROUP BY CONVERT(varchar, audited_datetime, 23)
            ORDER BY upload_date
        """
        
        _db = databaseconnection()
        results = _db.execute_Query(query)
        
        # Convert results to a dictionary with dates as keys
        datewise_counts = {}
        
        for result in results:
            # Ensure the date is used correctly as a key
            date_str = result['upload_date'][:10]  # Extract only the date part
            datewise_counts[date_str] = result['recCount']
        
        # Ensure all 7 days are represented, fill missing days with 0
        current_date = end_date
        while current_date <= start_date:
            current_date_str = current_date.strftime('%Y-%m-%d')
            if current_date_str not in datewise_counts:
                datewise_counts[current_date_str] = 0
            current_date += timedelta(days=1)
        
        return datewise_counts

    ##ends##

    def get_master_stats():
        #print("Hello We are here")
        query = "SELECT system_uploaded,system_processed,system_audited,system_failed FROM master_stats WITH (NOLOCK) "
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result[0]     

    def get_file_upload_count(self,company_code):
        query = "SELECT count(1) as recCount FROM user_invoices WITH (NOLOCK) where company_code = '" + str(company_code) +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        
        return result[0]["recCount"]         
    
    def get_processed_count(self,company_code):
        query = "SELECT count(1) as recCount FROM predicted_data WITH (NOLOCK) where predicted_status in ('1','2') and  company_code = '" + str(company_code) +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result[0]["recCount"]  
    
    def get_audited_count(self,company_code):
        query = "SELECT count(1) as recCount FROM audited_data WITH (NOLOCK) where audited_status = '3' and  company_code = '" + str(company_code) +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result[0]["recCount"]

    def get_digitized_count(self,company_code):
        query = "SELECT count(1) as recCount FROM user_scan_invoices WITH (NOLOCK) where status = '2' and  company_code = '" + str(company_code) +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result[0]["recCount"]

    def get_classifire_count(self,company_code):
        query = "SELECT count(1) as recCount FROM user_classification_invoices WITH (NOLOCK) where company_code = '" + str(company_code) +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result[0]["recCount"]  

    def last_login(self,user_id):
        user = User.objects.get(id=user_id)
        last_login=str(user.last_login).split(".")[0]
        return last_login 

    def last_process(self,company_code):
        query = "SELECT top(1) created_datetime FROM predicted_data WITH (NOLOCK) where  company_code = '" + str(company_code) +"' order by predicted_id desc"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        #print("Predicted Data", result[0]["created_datetime"])
        if result:           
            return result[0]["created_datetime"]
        else:
            return ""
           
    def process_datewise(self,company_code):
        query = "SELECT count(predicted_id) as total_count, CONCAT(DATEPART(MONTH, CONVERT(VARCHAR(10),created_datetime,112)), '/', DATEPART(DD, CONVERT(VARCHAR(10),created_datetime,112)))  as datemonth  FROM predicted_data  WHERE  company_code = '" + str(company_code) +"' AND  CONVERT(VARCHAR(10),created_datetime,112) > DATEADD(DAY, -15, GETDATE())  GROUP BY CONVERT(VARCHAR(10),created_datetime,112) "
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        #print("Predicted Data", result)
        if result:           
            return result
        else:
            return ""
            
    def audit_datewise(self,company_code):
        query = "SELECT count(audited_id) as total_count, CONCAT(DATEPART(MONTH, CONVERT(VARCHAR(10),audited_datetime,112)), '/', DATEPART(DD, CONVERT(VARCHAR(10),audited_datetime,112)))  as datemonth  FROM audited_data  WHERE  company_code = '" + str(company_code) +"' AND  CONVERT(VARCHAR(10),audited_datetime,112) > DATEADD(DAY, -15, GETDATE()) GROUP BY CONVERT(VARCHAR(10),audited_datetime,112) "
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        #print("Predicted Data", result)
        if result:           
            return result
        else:
            return ""             
        
          

    def get_failed_by_idp_count(self,company_code):
        query = "SELECT count(1) as recCount FROM user_invoices WITH (NOLOCK) where status = '4' and  company_code = '" + str(company_code) +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result[0]["recCount"]

    def dashboard_configuration_list(self,user_id,company_code):
        objcustom  = customfields()
        query = "SELECT config_uuid,config_name,is_active from form_fields_master WITH (NOLOCK) where company_code = '" + company_code + "'"; 
        _db = databaseconnection()
        config_list = _db.execute_Query(query)
        #dict_config = []
        
        #for config in config_liswt:
            
            #fieldsConfiguration = objcustom.get_custom_fields_by_uuid(config["config_uuid"],user_id,company_code)
            #dict_config.append({"config_name" : config["config_name"],"config_data" : fieldsConfiguration})
       
        return config_list  

    def get_botdata(self,pk):
        #print("Hello We are here")
        query = "SELECT file_name,user_id,config_uuid  FROM predicted_data WITH (NOLOCK) where predicted_uuid = '" + str(pk) +"'"  
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result[0]
     


    def get_register_user(self,company_code):
        query = "SELECT count(1) as recCount FROM auth_user WITH (NOLOCK) where company_code = '" + str(company_code) +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result[0]["recCount"]


    def active_supplier(self,company_code):
        query = "SELECT count(1) as recCount FROM stp_supplier WITH (NOLOCK) where company_code = '" + str(company_code) +"' and supplier_status='1'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result[0]["recCount"]