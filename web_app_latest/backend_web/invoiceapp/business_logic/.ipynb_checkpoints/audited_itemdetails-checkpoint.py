from invoiceapp.db_operations.databaseconnection import databaseconnection
from datetime import datetime
from invoiceapp.business_logic.customfields import customfields
import pandas as pd

class audited_itemdetails:   
    def __init__(self):
        pass     
    def mapping_fields(self,user_id,field_type,config_id,company_code):
        fields_name = ""
        objcustom  = customfields()
        results = objcustom.get_standard_fields_mapping(user_id,field_type,config_id,company_code)
        if(field_type == "S"):
            fields_name = results["standard_list"]
        elif(field_type == "SC"):
            fields_name = results["standard_custom_list"]
        elif(field_type == "T"):
            fields_name = results["table_list"]
        elif(field_type == "TC"):
            fields_name =  results["table_custom_list"]
         
        return fields_name
    
    def mapping_custom_field_for_report(self,user_id,field_type,config_id,company_code):
        fields_name = ""
        objcustom  = customfields()
        results = objcustom.get_fields_for_report(user_id,field_type,config_id,company_code)
         
        return results
    
    
     
    def get_config_uuid(self,predicted_uuid):
        query = "SELECT config_uuid as config_uuid FROM audited_data WITH (NOLOCK) where uuid = '" + str(predicted_uuid) +"'"  
        _db = databaseconnection()
        # print(query,"++++++++===========")
        result = _db.execute_Query(query) 
        # print(result,"llllllllllllllll")
        if len(result) > 0 :
            return result[0]["config_uuid"]
        else:
            return ""
        

    def get_file_uuid(self,predicted_uuid):
        query = "SELECT file_uuid as file_uuid FROM audited_data WITH (NOLOCK) where uuid = '" + str(predicted_uuid) +"'"  
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        if len(result) > 0 :
            return result[0]["file_uuid"]
        else:
            return ""
        return result[0]["file_uuid"]

    
    def get_config_uuid_by_user_id(self,user_id):
        query = "SELECT config_uuid as config_uuid FROM form_fields_master WITH (NOLOCK) where user_id = '" + str(user_id) +"'"  
        _db = databaseconnection()
        # print(query,"---===")
        result = _db.execute_Query(query)
        # print(result,"$$$$$")
        return result[0]["config_uuid"]
    def get_standard_data_withoutscore(self,rec_id, file_id,user_id,company_code):
         
        config_id = self.get_config_uuid(rec_id) 
        
         
        fields_name = self.mapping_fields(user_id,"S",config_id,company_code)
        custom_fields = self.mapping_fields(user_id,"SC",config_id,company_code) 
         
        if(custom_fields != ""):
            fields_name = fields_name + "," + custom_fields 
        
        query = "SELECT user_id,config_uuid,uuid," + fields_name + " from audited_data WITH (NOLOCK) where uuid = '" + rec_id + "'"; 
        _db = databaseconnection()
         
        result = _db.execute_Query(query) 
        return result

    def get_standard_data(self,rec_id, file_id,user_id,company_code):
         
        config_id = self.get_config_uuid(rec_id) 
        # print(config_id,"eeeeeeeeeeeeeeeeeeeeeeee")
         
        fields_name = self.mapping_fields(user_id,"S",config_id,company_code)
        custom_fields = self.mapping_fields(user_id,"SC",config_id,company_code) 
        fields_name = fields_name.replace("file_name","original_file_name")
        if(custom_fields != ""):
            fields_name = fields_name + "," + custom_fields
         
        
        fields_conf_score = fields_name.replace(",",",conf_")
        fields_conf_score = fields_conf_score.replace("original_file_name","conf_file_name")
        query = "SELECT company_code, user_id,config_uuid,uuid," + fields_name + ", " + fields_conf_score + "  from audited_data WITH (NOLOCK) where uuid = '" + rec_id + "'"; 
        _db = databaseconnection()
        # print(query, "a_debug")
        result = _db.execute_Query(query) 
        print(result)
        return result
    
    def get_table_data(self,rec_id, file_id,user_id,company_code):
        config_id = self.get_config_uuid(rec_id)        
        
        fields_name = self.mapping_fields(user_id,"T",config_id,company_code)        
        
        if self.mapping_fields(user_id,"TC",config_id,company_code) != "":
            if(fields_name != ""):
                fields_name = fields_name + ","+self.mapping_fields(user_id,"TC",config_id,company_code)
            else:
                fields_name = self.mapping_fields(user_id,"TC",config_id,company_code)
        else:
            fields_name = fields_name 
         
        # print(fields_name)
        if(fields_name != ""):
            query = "SELECT " + fields_name + "  from audited_table_data WITH (NOLOCK) where uuid = '" + rec_id + "'"; 
            _db = databaseconnection()
            print(query)
            result = _db.execute_Query(query)
            return result
        else:
            return ''

    def get_audit_data_by_date(self, user_id,rec_id,from_date,to_date):
        config_id = self.get_config_uuid(rec_id)        
         
        fields_name = self.mapping_fields(user_id,"S",config_id)
        custom_fields = self.mapping_fields(user_id,"SC",config_id) 
        #print("HAPPY ", custom_fields)
        if(custom_fields != ""):
            fields_name = fields_name + "," + custom_fields
         
        
        fields_conf_score = fields_name.replace(",",",conf_")
        fields_conf_score = fields_conf_score.replace("file_name","conf_file_name")
        query = "SELECT user_id,config_uuid,uuid," + fields_name + ", " + fields_conf_score + "  from audited_data WITH (NOLOCK) where "
        query = query + " uuid = '" + rec_id + "'"; 
        _db = databaseconnection()
         
        result = _db.execute_Query(query) 
        return result
    
    def parse_header(self,headers):
        data = headers.split(',') #split string into a list
        header = []
        for temp in data:
            header.append(temp.split('as')[-1])
        return header
    

    def Download_accuracy_Report(self, user_id,template_id,from_date,to_date,company_code):
        try:

            config_id = template_id     
            query = "select file_name as 'File Name',accuracy_percent as Accuracy from accuracy_info  ai WITH (NOLOCK) inner join user_invoices ui WITH (NOLOCK) on ai.file_uuid = ui.invoice_uid "  
             
            query = query + " where "
             

            if(from_date != "" and to_date != ""):
                start_date = datetime.strptime(from_date ,"%m/%d/%Y").date()
                end_date = datetime.strptime(to_date ,"%m/%d/%Y").date()
                query +=  " ( CONVERT(varchar(10),ai.accuracy_date, 23) between '" + datetime.strftime(start_date, '%Y-%m-%d') + "' and '" + datetime.strftime(end_date, '%Y-%m-%d') +"' ) and "
            if(config_id != ""):
                query = query + " ui.config_id = '" + config_id + "' and " 
            
            query = query + " ui.company_code = '" + company_code + "'" 
            #print(query)
            _db = databaseconnection()         
            result = _db.execute_Query(query) 
            df = pd.DataFrame.from_records(result)
             
            return df
        except Exception as e:
            print(str(e))

    def Download_deleted_Report(self, user_id,template_id,from_date,to_date,company_code):
        try:
            config_id = template_id     
            
            query = "SELECT file_name as 'File Name', ( CONVERT(varchar(10),deleted_datetime, 101)) as 'Deleted Date' , ISNULL(first_name,'') AS 'First Name' , ISNULL(last_name,'') AS 'Last Name' , username as 'User Name'   "
            
            query = query + " from deleted_data WITH (NOLOCK) inner join auth_user WITH (NOLOCK) on deleted_data.deleted_by = auth_user.id"  
             
            query = query + " where "
             

            if(from_date != "" and to_date != ""):
                start_date = datetime.strptime(from_date ,"%m/%d/%Y").date()
                end_date = datetime.strptime(to_date ,"%m/%d/%Y").date()
                query +=  " ( CONVERT(varchar(10),deleted_datetime, 23) between '" + datetime.strftime(start_date, '%Y-%m-%d') + "' and '" + datetime.strftime(end_date, '%Y-%m-%d') +"' ) and "
             
            query = query + " deleted_data.company_code = '" + company_code + "'" 
            #print(query)
            _db = databaseconnection()         
            result = _db.execute_Query(query) 
            df = pd.DataFrame.from_records(result)
             
            return df
        except Exception as e:
            print(str(e))
    def Download_User_Invoice_Report(self, user_id,template_id,from_date,to_date,company_code):
        try:
            config_id = template_id     
            
            query = "SELECT file_name as 'File Name' , ( CONVERT(varchar(10),user_invoices.updated_datetime, 101)) as 'Uploaded Date' "
            query = query +  ", CASE WHEN status =1  THEN 'Pending' WHEN status = 2 THEN 'Ready to validate' "
            query = query + " WHEN status = 3 THEN 'Audit Completed' WHEN status = 4 THEN 'Error' END  as 'Status' "
            query = query + " from user_invoices WITH (NOLOCK)"  
             
            query = query + " where "
             

            if(from_date != "" and to_date != ""):
                start_date = datetime.strptime(from_date ,"%m/%d/%Y").date()
                end_date = datetime.strptime(to_date ,"%m/%d/%Y").date()
                query +=  " ( CONVERT(varchar(10),user_invoices.updated_datetime, 23) between '" + datetime.strftime(start_date, '%Y-%m-%d') + "' and '" + datetime.strftime(end_date, '%Y-%m-%d') +"' ) and "
            if(config_id != ""):
                query = query + " user_invoices.config_id = '" + config_id + "' and " 
            
            query = query + " user_invoices.company_code = '" + company_code + "'" 
            #print(query)
            _db = databaseconnection()         
            result = _db.execute_Query(query) 
            df = pd.DataFrame.from_records(result)
             
            return df
        except Exception as e:
            print(str(e))

    def Download_Predict_Report(self, user_id,template_id,from_date,to_date,company_code):
        try:

            config_id = template_id     
         
            fields_name = self.mapping_custom_field_for_report(user_id,"S",config_id,company_code)
            custom_fields = self.mapping_custom_field_for_report(user_id,"SC",config_id,company_code) 

            table_fields_name = self.mapping_custom_field_for_report(user_id,"T",config_id,company_code)
            table_custom_fields = self.mapping_custom_field_for_report(user_id,"TC",config_id,company_code) 

            
            if(custom_fields != ""):
                fields_name = fields_name[1:] +  custom_fields 
                
            if(table_fields_name != ""):    
                fields_name = fields_name +  table_fields_name 
            
            if(table_custom_fields != ""):
                fields_name = fields_name +  table_custom_fields
 
            fields_name = fields_name.strip(",")
            query = "SELECT original_file_name as 'Main File'," + fields_name + "  from predicted_data WITH (NOLOCK) left join "  
            query = query + " predicted_table_data WITH (NOLOCK) on predicted_table_data.predicted_uuid = predicted_data.predicted_uuid "
            query = query + " where "
             

            if(from_date != "" and to_date != ""):
                start_date = datetime.strptime(from_date ,"%m/%d/%Y").date()
                end_date = datetime.strptime(to_date ,"%m/%d/%Y").date()
                query +=  " ( CONVERT(varchar(10),predicted_data.created_datetime, 23) between '" + datetime.strftime(start_date, '%Y-%m-%d') + "' and '" + datetime.strftime(end_date, '%Y-%m-%d') +"' ) and "
            if(config_id != ""):
                query = query + " predicted_data.config_uuid = '" + config_id + "' and " 
            
            query = query + " predicted_data.company_code = '" + company_code + "'" 
            
            query = query.replace("invoice_address as","predicted_data.invoice_address as ")
            query = query.replace("total_amount as","predicted_table_data.total_amount as ")
            query = query.replace("supplier_pan as","predicted_data.supplier_pan as ")
            _db = databaseconnection()     
            # print(query)    
            result = _db.execute_Query(query) 
            df = pd.DataFrame.from_records(result)
             
            return df
        except Exception as e:
            print(str(e))
            
            
    def Download_Audit_Report(self, user_id,template_id,from_date,to_date,company_code):
        try:

            config_id = template_id     
         
            fields_name = self.mapping_custom_field_for_report(user_id,"S",config_id,company_code)
            custom_fields = self.mapping_custom_field_for_report(user_id,"SC",config_id,company_code) 

            table_fields_name = self.mapping_custom_field_for_report(user_id,"T",config_id,company_code)
            table_custom_fields = self.mapping_custom_field_for_report(user_id,"TC",config_id,company_code) 

            
            if(custom_fields != ""):
                fields_name = fields_name[1:] +  custom_fields 
                
            if(table_fields_name != ""):    
                fields_name = fields_name +  table_fields_name 
            
            if(table_custom_fields != ""):
                fields_name = fields_name +  table_custom_fields
            fields_name = fields_name.strip(",")
            query = "SELECT original_file_name as 'Main File'," + fields_name + "  from audited_data WITH (NOLOCK) left join  audited_table_data WITH (NOLOCK) on audited_table_data.UUID = audited_data.UUID "
            query = query + " where "
             

            if(from_date != "" and to_date != ""):
                start_date = datetime.strptime(from_date ,"%m/%d/%Y").date()
                end_date = datetime.strptime(to_date ,"%m/%d/%Y").date()
                query +=  " ( CONVERT(varchar(10),audited_datetime, 23) between '" + datetime.strftime(start_date, '%Y-%m-%d') + "' and '" + datetime.strftime(end_date, '%Y-%m-%d') +"' ) and "
            if(config_id != ""):
                query = query + " audited_data.config_uuid = '" + config_id + "' and " 
            
            query = query + " audited_data.company_code = '" + company_code + "'" 
            
          
            query = query.replace("total_amount as","audited_table_data.total_amount as ")
            print(query)
            _db = databaseconnection()         
            result = _db.execute_Query(query) 
            df = pd.DataFrame.from_records(result)
             
            return df
        except Exception as e:
            print(str(e))

    def Excel_Data_Templatewise(self, user_id,template_id,from_date,to_date,action_for,company_code):
        if action_for == "audit_report":
            print("Hello here")
            return self.Download_Audit_Report( user_id,template_id,from_date,to_date,company_code)
        elif action_for == "predict_report":
            return self.Download_Predict_Report( user_id,template_id,from_date,to_date,company_code)
        elif action_for == "user_invoice_report":
            return self.Download_User_Invoice_Report( user_id,template_id,from_date,to_date,company_code) 
        elif action_for == "accuracy_report":
            return self.Download_accuracy_Report( user_id,template_id,from_date,to_date,company_code) 
        elif action_for == "deleted_report":
            return self.Download_deleted_Report( user_id,template_id,from_date,to_date,company_code) 

            


            

    def Excel_Data(self, user_id,rec_id,from_date,to_date,company_code):
        try:
            print("Hello in code")
            config_id = self.get_config_uuid(rec_id) 
            #print(config_id)
            #print("Config Id not found")
            if config_id != "":
                fields_name = self.mapping_custom_field_for_report(user_id,"S",config_id,company_code)
                
                custom_fields = self.mapping_custom_field_for_report(user_id,"SC",config_id,company_code) 

                table_fields_name = self.mapping_custom_field_for_report(user_id,"T",config_id,company_code)
                
                table_custom_fields = self.mapping_custom_field_for_report(user_id,"TC",config_id,company_code) 

                
                if(custom_fields != ""):
                    fields_name = fields_name[1:] +  custom_fields

                if(table_fields_name != ""):
                    fields_name = fields_name +  table_fields_name
                
                if(table_custom_fields != ""):
                    fields_name = fields_name +  table_custom_fields
    
                fields_name = fields_name.strip(',')
                
                # print("@@@@@@@@@@@",fields_name)
                query = "SELECT original_file_name as 'Main File', " + fields_name + "  from audited_data WITH (NOLOCK) left join  audited_table_data WITH (NOLOCK) on audited_table_data.UUID = audited_data.UUID "
                query = query + " where "
                

                if(from_date != "" and to_date != ""):
                    query +=  " ( CONVERT(varchar(10),created_datetime, 23) between '" + from_date + "' and '" + to_date+"' ) and "
                if(rec_id != ""):
                    query = query + " audited_data.uuid = '" + rec_id + "' and " 
                
                query = query + " audited_data.company_code = '" + company_code + "'" 
                query = query.replace("total_amount as","audited_table_data.total_amount as ")
                query = query.replace("supplier_pan as","audited_table_data.supplier_pan as ")
                _db = databaseconnection()  
                print("Inside code query",query)       
                result = _db.execute_Query(query) 
                #print("@@@@@@@@@@@@",result)
                df = pd.DataFrame.from_records(result)
                #print("############")
                #header_data = self.parse_header(fields_name)
                header_data = self.parse_header(fields_name)
                print(header_data)
                df.headers = header_data
                # print("############@@@@@@@@@@@@@@@@@")
                return df
            else:
                df = pd.DataFrame.from_records("")
                df.headers = ""
                return df
        except Exception as e:
            print(str(e))



