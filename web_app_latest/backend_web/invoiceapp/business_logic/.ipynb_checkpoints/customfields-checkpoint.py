from invoiceapp.db_operations.databaseconnection import databaseconnection
from datetime import datetime

from invoiceapp.business_logic.site_settings import site_settings
import uuid

class customfields:   
    def __init__(self):
        pass     
    def SQL_INJECTION_CHECK(self,query):
        restricted_list = ["Drop","Alter","truncate","1=1"]
        ##print("calling sql ")
        res = [ele.lower() for ele in restricted_list if(ele.lower() in query.lower())] 
        #print(res)       
        if(len(res) > 0):
            is_invalid = True
        else:
            is_invalid = False
        return is_invalid

    def get_configurations_List(self,user_id,company_code):

        query = "SELECT config_name, id, config_uuid from form_fields_master WITH (NOLOCK) where company_code = '" + company_code + "'"; 
        _db = databaseconnection()
        result = _db.execute_Query(query)
         
        return result 

    def validate_layout_count(self,user_id,company_code):
        # Validate is user allowed to add config
        config_list =  site_settings.get_configuration_list(user_id,company_code)
        if len(config_list) == 0:
            config_list =  site_settings.get_default_settings()
         
        allow_layout = 0
        for field in config_list:
            if field["setting_name"] =="max_layout_count":
                allow_layout = field["setting_value"]
        
        #print("Max config allowed", str(allow_layout))
        query = "SELECT count(1) as recCount FROM form_fields_master WITH (NOLOCK) where company_code = '" + str(company_code) +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        number_layout = int(result[0]["recCount"])
        #print("Numner of layout ", str(number_layout))
        if(int(allow_layout) <= number_layout):
            return False
        else:
            return True

    
    def get_all_config(user_id):
        query = "SELECT fields_name,field_key,field_type from form_fields WITH (NOLOCK) where customer_code = '" + customer_code + "'"; 
        _db = databaseconnection()
        result = _db.execute_Query(query)
         
        return result 

    def get_fields_names(self,user_id,ftype,config_uuid):
        
        query = "SELECT fields_name  from form_fields_mapping WITH (NOLOCK)  where field_type = '" + ftype + "' and user_id = '" + str(user_id) + "' and config_uuid =  '" + str(config_uuid) + "' order by field_sequence"
         
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result 
         

    def get_standard_fields_mapping(self,user_id,ftype,config_uuid,company_code):
        
        query = "SELECT fields_name,field_key,field_type,field_sequence,mapped_field from form_fields_mapping WITH (NOLOCK)  where field_type = '" + ftype + "' and company_code = '" + str(company_code) + "' and config_uuid =  '" + str(config_uuid) + "' order by field_sequence" 
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        # print(result,"%%%%%%%%%%%%")
        output = self.get_fields_Names(result)
        # print(output,"^^^^^^^^^^^^^&&&&&&&&&&&&")
        return output

    def get_fields_for_report(self,user_id,ftype,config_uuid,company_code):
        
        query = "SELECT fields_name,field_key,field_type,field_sequence,mapped_field from form_fields_mapping WITH (NOLOCK)  where field_type = '" + ftype + "' and company_code = '" + str(company_code) + "' and config_uuid =  '" + str(config_uuid) + "' order by field_sequence"
         
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        output = self.get_fields_Names_for_reports(result) 
        return output

    def get_custom_fields_by_uuid(self,config_uuid,user_id,company_code):
        query = "SELECT fields_name,field_key,field_type,field_sequence,mapped_field from form_fields_mapping WITH (NOLOCK) where config_uuid = '" + str(config_uuid) + "' and company_code = '"+ company_code+"' order by field_sequence"; 
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        output = self.get_display_list(result)         
        return output


    def get_custom_fields(self,user_id,config_uuid,company_code):
        query = "SELECT fields_name,field_key,field_type,field_sequence,mapped_field from form_fields_mapping WITH (NOLOCK) where company_code = '" + str(company_code) + "' and config_uuid =  '" + str(config_uuid) + "'  order by field_sequence"; 
        _db = databaseconnection()
        # print(query,"##$$%%^^&&")
        result = _db.execute_Query(query) 
        
        output = self.get_display_list(result)         
        return output
    
    
    def get_fields_Names(self,dbList):
        standard_fields = ""
        standard_custom_fields = ""
        table_fields = ""
        table_custom_fields = ""
        for field_map in dbList:
            if(field_map["field_type"]=='S'):
                standard_fields = standard_fields + "," +  field_map["field_key"]
            if(field_map["field_type"]=='SC'):
                standard_custom_fields = standard_custom_fields + "," +  field_map["mapped_field"]
            if(field_map["field_type"]=='T'):
                table_fields = table_fields + "," +  field_map["field_key"]
            if(field_map["field_type"]=='TC'):
                table_custom_fields = table_custom_fields + "," +  field_map["mapped_field"]

        refine_list= { 'standard_list':standard_fields[1:],'standard_custom_list':standard_custom_fields[1:],'table_list':table_fields[1:],'table_custom_list':table_custom_fields[1:] }
         
        return refine_list
    
    def get_fields_Names_for_reports(self,dbList):
        standard_fields = ""
        standard_custom_fields = ""
        table_fields = ""
        table_custom_fields = ""
        for field_map in dbList:
            if( field_map["fields_name"] == "delivery address"):
                table_custom_fields = table_custom_fields + "," +  field_map["mapped_field"] + " as 'Ship to Address'"            
            elif( field_map["fields_name"] == "invoice address"):
                table_custom_fields = table_custom_fields + "," +  field_map["mapped_field"] + " as 'Bill to Address'" 
            else:
                #add by Pradeep
                table_custom_fields = table_custom_fields + "," +  field_map["mapped_field"] + " as '" + field_map["fields_name"] + "'"       
         
        return table_custom_fields
            

    def get_display_list(self,dbList):
        standard_list=[]
        standard_custom_list=[]
        table_list=[]
        table_custom_list=[]
        for field_map in dbList:
            if(field_map["field_type"]=='S'):
                standard_list.append(field_map)
            if(field_map["field_type"]=='SC'):
                standard_custom_list.append(field_map)
            if(field_map["field_type"]=='T'):
                table_list.append(field_map)
            if(field_map["field_type"]=='TC'):
                table_custom_list.append(field_map)
        refine_list= { 'standard_list':standard_list,'standard_custom_list':standard_custom_list,'table_list':table_list,'table_custom_list':table_custom_list  }
        return refine_list


   

    def is_config_exist(self,company_code,config_name):
        query = "SELECT count(1) as recCount FROM form_fields_master WITH (NOLOCK) where company_code = '" + str(company_code) +"' and config_name = '" + config_name + "'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
         
        if(result[0]["recCount"] >= 1):
            return True
        else:
            return False 

    def get_fileds_other(self, input):
        #print(input)
        try:
            str_arr = input.split()  
            if(len(str_arr) > 1):
                return str_arr[1]
            else:
                return ""
        except Exception as e:
            print(str(e))

    def generate_field(self,user_id,field_type,info,prompt,tablemapping,config_UUID,company_code):
        query = ""
        db_prompt = ""
          
        for i, val in enumerate(info):
            main_value = ""
            option_value = ""
            if field_type == 'S':
                str_arr = val.split("|")
                main_value = str_arr[0].replace("_"," ").replace("|","")
                field_data_type = str_arr[1] 
                mappingval = str_arr[0]
            elif field_type == 'T':
                str_arr = val.split("|")
                main_value = str_arr[0].replace("_"," ")
                field_data_type= ""
                option_value = str_arr[1]
                mappingval = str_arr[0].replace(" ","_")
            elif field_type == 'TC':
                str_arr = val.split("|")
                main_value = str_arr[0].replace("_"," ")
                field_data_type = ""
                option_value = str_arr[1]
                mappingval = tablemapping+"_"+ str(i+1)
                if prompt:
                    db_prompt = prompt[i].replace("\'", "\'\'")
            else:                
                str_arr = val.split("|")
                main_value = str_arr[0].replace("_"," ")
                field_data_type = str_arr[1]
                option_value = ""
                mappingval = tablemapping+"_"+ str(i+1)
                if prompt:
                    db_prompt = prompt[i].replace("\'", "\'\'")
            
            query = query +  ",('" + user_id + "',"
            query = query +  "'" + main_value.replace("|","") + "',"
            query = query +  "'" + main_value.replace(" ","_").replace("|","") + "',"
            query = query +  "'" + field_type + "',"
            query = query +  "'" + db_prompt + "',"
            query = query +  "'" + mappingval.replace("|","") + "',"+ str(i+1)+",'"+ config_UUID +"','"+ option_value +"','"+ field_data_type +"','"+ company_code +"')"
        print("**********************************************************")
        print(query)
        return query


    def delete_config(self,user_id,configuration_uuid):
        
        objquery = "select id from auth_user where company_code=(select company_code from auth_user where id= '"+user_id+ "')"
        _db = databaseconnection()
        
        result = _db.execute_Query(objquery)
        ids=''
        for x in result:
            ids += str(x['id']) + ','
        user_ids = ids[:-1]    
        
        query = "Delete from form_fields_mapping where user_id IN(" + user_ids + ") and config_uuid = '" + configuration_uuid + "' ; "
        query = query + " Delete from form_fields_master where user_id IN(" + user_ids + ") and config_uuid = '" + configuration_uuid + "' ; "
        query = query + " Delete from user_invoices where user_id IN(" + user_ids + ") and config_id = '" + configuration_uuid + "' ; "
        query = query + " Delete from predicted_table_data where user_id IN(" + user_ids + ") and config_uuid = '" + configuration_uuid + "' ; "
        query = query + " Delete from predicted_data where user_id IN(" + user_ids + ") and config_uuid = '" + configuration_uuid + "' ; "
        query = query + " Delete from audited_table_data where  config_uuid = '" + configuration_uuid + "'; "
        query = query + " Delete from audited_data where user_id IN(" + user_ids + ") and config_uuid = '" + configuration_uuid + "' ; "
        #print("@@@@@@@@@@@@@@", query)
        _db = databaseconnection()
        _db.execute_non_query(query)

    # def add_config(self,user_id,config_name,config_UUID,company_code):
    #     insert_query = "Insert into form_fields_master(user_id,config_name,config_uuid, is_active,is_deleted,company_code) Values " +  "('" + user_id + "', '" + config_name+ "','" + config_UUID + "', '1' , '0','" + company_code + "')"
         
    #     if not self.SQL_INJECTION_CHECK(insert_query):
    #         #print(insert_query)
    #         _db = databaseconnection()
    #         _db.execute_non_query(insert_query)
    #         return ''
    #     else:
    #         return "Miscellaneous Action found" 

    def add_config(self,user_id,config_name,config_UUID,prompt_text, company_code):
        insert_query = "Insert into form_fields_master(user_id,config_name,config_uuid, config_prompt, is_active,is_deleted,company_code) Values " +  "('" + user_id + "', '" + config_name+ "','" + config_UUID + "', '" + prompt_text+ "', '1' , '0','" + company_code + "')"
         
        if not self.SQL_INJECTION_CHECK(insert_query):
            #print(insert_query)
            _db = databaseconnection()
            _db.execute_non_query(insert_query)
            return ''
        else:
            return "Miscellaneous Action found" 

    # def add_standard_fields_config(self,UUID,user_id,static_fields,static_custom_fields,table_static_fields,table_custom_fields,config_name,static_custom_datatype,company_code):
       
    #     comma = "','"
    #     # Add Config
    #     output = self.add_config(user_id,config_name,UUID,company_code)
    #     if output == "Miscellaneous Action found":
    #         return "Miscellaneous Action found" 
    #     else:
    #         # Add Config Details
    #         static_fields_names = comma.join(static_fields)
    #         # Create fields Name
    #         standard_field = self.generate_field(user_id,"S",static_fields,"std",UUID,company_code)
    #         standard_custom_field = self.generate_field(user_id,"SC",static_custom_fields,"s",UUID,company_code)
    #         table_field = self.generate_field(user_id,"T",table_static_fields,"tbl",UUID,company_code)
    #         table_custom_field = self.generate_field(user_id,"TC",table_custom_fields,"t",UUID,company_code)
            
    #         fields_set =  standard_field[1:] + standard_custom_field  + table_field  + table_custom_field
            
    #         standard_query = "Insert into form_fields_mapping(user_id,fields_name,field_key,field_type,mapped_field,field_sequence,config_uuid,field_options,field_data_type,company_code) Values"
    #         standard_query = standard_query + fields_set 
            
    #         if not self.SQL_INJECTION_CHECK(standard_query):
    #            _db = databaseconnection()
    #            _db.execute_non_query(standard_query)
    #            return '' 
    #         else:
    #             self.delete_config(user_id,UUID)
    #             return "Miscellaneous Action found" 

    def add_standard_fields_config(self,UUID,user_id,static_fields,static_custom_fields,table_static_fields,table_custom_fields,prompt_custom_dict, prompt_table_custom_dict, config_name,static_custom_datatype,company_code, prompt_text=""):
       
        comma = "','"
        # Add Config
        output = self.add_config(user_id,config_name,UUID, prompt_text, company_code)
        if output == "Miscellaneous Action found":
            return "Miscellaneous Action found" 
        else:
            # Add Config Details
            static_fields_names = comma.join(static_fields)
            # Create fields Name
            standard_field = self.generate_field(user_id,"S",static_fields,"","std",UUID,company_code)
            standard_custom_field = self.generate_field(user_id,"SC",static_custom_fields,prompt_custom_dict,"s",UUID,company_code)
            table_field = self.generate_field(user_id,"T",table_static_fields,"", "tbl",UUID,company_code)
            table_custom_field = self.generate_field(user_id,"TC",table_custom_fields,prompt_table_custom_dict,"t",UUID,company_code)
            
            fields_set =  standard_field[1:] + standard_custom_field  + table_field  + table_custom_field
            
            standard_query = "Insert into form_fields_mapping(user_id,fields_name,field_key,field_type,mapped_prompt,mapped_field,field_sequence,config_uuid,field_options,field_data_type,company_code) Values"
            standard_query = standard_query + fields_set 
            
            if not self.SQL_INJECTION_CHECK(standard_query):
               _db = databaseconnection()
               _db.execute_non_query(standard_query)
               return '' 
            else:
                self.delete_config(user_id,UUID)
                return "Miscellaneous Action found" 

                


    # Business Rules Specific Function
    def get_standard_fields_by_uuid(config_uuid,user_id,field_data_type,company_code):
        query = "SELECT fields_name,field_key,mapped_field,field_type,field_data_type,field_sequence,mapped_field from form_fields_mapping WITH (NOLOCK) where field_type  IN ('S','SC') and config_uuid = '" + str(config_uuid) + "' and company_code = '"+ str(company_code)+"' and field_data_type = '"+ str(field_data_type)+"'  order by field_sequence"; 
        _db = databaseconnection()
        result = _db.execute_Query(query)  
        return result

    def get_fields_prompt(self, config_id, company_code):
        print(config_id,"##$$$------------------@@@@@@@@@@@@")
        query = "SELECT config_prompt from form_fields_master where config_uuid = '" + str(config_id) + "' and company_code = '"+ str(company_code)+"'";
        _db = databaseconnection()
        user_prompt = _db.execute_Query(query)
        print(user_prompt,"@@#####===========")
        if user_prompt[0]["config_prompt"]:
            query = "SELECT fields_name,field_key,mapped_prompt from form_fields_mapping WITH (NOLOCK) where field_type  IN ('SC') and config_uuid = '" + str(config_id) + "' and company_code = '"+ str(company_code)+"' order by field_sequence"; 
            _db = databaseconnection()
            header = _db.execute_Query(query)  
    
            query = "SELECT fields_name,field_key,mapped_prompt from form_fields_mapping WITH (NOLOCK) where field_type  IN ('TC') and config_uuid = '" + str(config_id) + "' and company_code = '"+ str(company_code)+"' order by field_sequence"; 
            _db = databaseconnection()
            table = _db.execute_Query(query)  
    

            return header, table
        else:
            return [], []
