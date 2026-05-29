from invoiceapp.db_operations.databaseconnection import databaseconnection
from datetime import datetime
from invoiceapp.business_logic.customfields import customfields


class predicted_items:   
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

    def get_config_uuid(self,predicted_uuid):
        query = "SELECT config_uuid as config_uuid FROM predicted_data WITH (NOLOCK) where predicted_uuid = '" + str(predicted_uuid) +"'"  
        print(query)
        _db = databaseconnection()
        result = _db.execute_Query(query) 
         
        return result[0]["config_uuid"]

    def get_file_uuid(self,predicted_uuid):
        query = "SELECT file_uuid as file_uuid FROM predicted_data WITH (NOLOCK) where predicted_uuid = '" + str(predicted_uuid) +"'"  
        _db = databaseconnection()
        result = _db.execute_Query(query) 
         
        return result[0]["file_uuid"]

    
    def get_config_uuid_by_user_id(self,user_id):
        query = "SELECT config_uuid as config_uuid FROM form_fields_master WITH (NOLOCK) where user_id = '" + str(user_id) +"'"  
        _db = databaseconnection()
        # print(query,"IIII")
        result = _db.execute_Query(query) 
        # print(result,"##EEE")
         
        return result[0]["config_uuid"]
    
    def get_next_id(self,previous_id,user_id,company_code):
        query = "SELECT top 1 predicted_uuid from predicted_data WITH (NOLOCK) where company_code = '" + str(company_code) +"' and  predicted_status = 1 and predicted_uuid not in ('" + previous_id + "')"; 
        _db = databaseconnection()
        #print(query)
        result = _db.execute_Query(query) 
        if(result):
            return result[0]["predicted_uuid"]
        else:
            return "" 

    def get_standard_data_withoutscore(self,rec_id, file_id,user_id,company_code):
         
        config_id = self.get_config_uuid(rec_id) 
        
         
        fields_name = self.mapping_fields(user_id,"S",config_id,company_code)
        custom_fields = self.mapping_fields(user_id,"SC",config_id,company_code) 
         
        if(custom_fields != ""):
            fields_name = fields_name + "," + custom_fields
         
        

        
        query = "SELECT user_id,config_uuid,predicted_uuid," + fields_name + " from predicted_data WITH (NOLOCK) where predicted_uuid = '" + rec_id + "'"; 
        _db = databaseconnection()
         
        result = _db.execute_Query(query) 
        return result

    def get_standard_data(self,rec_id, file_id,user_id,company_code):
         
        config_id = self.get_config_uuid(rec_id) 
        
         
        fields_name = self.mapping_fields(user_id,"S",config_id,company_code)
        custom_fields = self.mapping_fields(user_id,"SC",config_id,company_code) 
         
        if(custom_fields != ""):
            fields_name = fields_name + "," + custom_fields
         
        
        fields_conf_score = fields_name.replace(",",",conf_")
        fields_conf_score = fields_conf_score.replace("file_name","conf_file_name")
        query = "SELECT original_file_name,user_id,company_code,config_uuid,predicted_uuid," + fields_name + ", " + fields_conf_score + "  from predicted_data WITH (NOLOCK) where predicted_uuid = '" + rec_id + "'"; 
        # print(query)
        _db = databaseconnection()
         
        result = _db.execute_Query(query) 
        # print("@#@#@#@#@#@#@#@#@#",result)
        return result
    
    def get_table_data(self,rec_id, file_id,user_id,company_code):
        config_id = self.get_config_uuid(rec_id)
        # print(config_id,"###$$$$$$$$$$")
        
        
        fields_name = self.mapping_fields(user_id,"T",config_id,company_code)
        custom_fields = self.mapping_fields(user_id,"TC",config_id,company_code)
         
        if self.mapping_fields(user_id,"TC",config_id,company_code) != "":
            fields_name = fields_name + ","+ self.mapping_fields(user_id,"TC",config_id,company_code)
        else:
            fields_name = fields_name 
        
        fields_name = fields_name.strip(",")
        #print(fields_name)
        if(fields_name != ""):
            query = "SELECT " + fields_name + "  from predicted_table_data WITH (NOLOCK) where predicted_uuid = '" + rec_id + "'"; 
            _db = databaseconnection()
            result = _db.execute_Query(query)
            #print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",result)
            return result
        else:
            return ''

