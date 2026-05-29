from invoiceapp.db_operations.databaseconnection import databaseconnection
from datetime import datetime
import uuid



class processed_items:   
    def __init__(self):
        pass     
    def SQL_INJECTION_CHECK(self,query):
        restricted_list = ["Alter","truncate","1=1"]
         
        res = [ele for ele in restricted_list if(ele.lower() in query.lower())]        
        if(len(res) > 0):
            is_invalid = True
        else:
            is_invalid = False
        return is_invalid
        
    def get_data(customer_code,user_id):
        #query = "SELECT fields_name,field_key,field_type from form_fields where customer_code = '" + customer_code + "'"; 
        #_db = databaseconnection()
        #result = _db.execute_Query(query)
        processed_Data  = [{"id" : "1001","invoice_name":"90000","processed_datetime":"10/20/20 10:10:10 AM","status": "Pending","processed_by": "User"}]  
        return processed_Data

    def update_predict_status(predicted_uuid,status,user_id):
        UpdateQuery="UPDATE predicted_data SET predicted_status='"+ status +"', user_id = '"+ str(user_id) +"' WHERE predicted_uuid='" +predicted_uuid+ "'"
        _db = databaseconnection()
        _db.execute_non_query(UpdateQuery)
         
    def get_all_standard_data(user_id,company_code): 
        query = "SELECT predicted_id,first_name,last_name, original_file_name, predicted_uuid ,user_id,file_name,po_number,invoice_date,created_datetime,predicted_status,config_uuid,doc_type,invoice_number from predicted_data WITH (NOLOCK) "
        query = query + " inner join auth_user WITH (NOLOCK) on auth_user.id = predicted_data.user_id "
        query = query + " where predicted_status in(1,2)  and predicted_data.company_code = '" + company_code + "' order by created_datetime DESC";
       
        _db = databaseconnection()
        # print(query)
        result = _db.execute_Query(query) 
        return result
          
    def stringFormate(data):

        data=str(data)
        formatedata=data.replace("\'","\'\'")
        return formatedata
        
    def free_invoice(status,user_id):
        UpdateQuery="UPDATE predicted_data SET predicted_status='"+ status +"'  WHERE user_id='" + str(user_id) + "' and predicted_status = 2 "
        _db = databaseconnection()
        _db.execute_non_query(UpdateQuery)

    def is_inprogress(predicted_uuid,user_id):
        query = "SELECT user_id,first_name, last_name , predicted_status  from predicted_data p WITH (NOLOCK)  inner join auth_user WITH (NOLOCK) on auth_user.id = p.user_id where   predicted_uuid='" + predicted_uuid+ "'"; 
        _db = databaseconnection()
        print(query,"^^^%%")
        result = _db.execute_Query(query) 
        return result

    def save_idp_output(self,user_id,config_uuid,staticDict,dynamicDict,UUID,file_uuid,company_code):

       
        audit_data_key=''
        audit_data_value=''
        conf_score = ''
        conf_key = ''
        original_file_name = ''
        for key, value in staticDict.items():
            audit_data_key += key +','   
            conf_key += "conf_" + key  +','
            if key == 'file_name' :
                audit_data_value += "'" + value[0].replace("null", "").replace("\'","\'\'") + "' , "
                original_file_name =  value[0].replace("null", "").replace("\'","\'\'")
            else:
                val = value[0].replace("null","") 
                val = val.replace("None","") 
                audit_data_value +=  "'" + val.replace("\'","\'\'") + "' , "
            try:
                conf_value = str(value[1]).replace("NA","")
                conf_score +=   "'" + conf_value + "' , "
            except Exception as e:
                print(e)
            # print(conf_score)

        
        header_lenth = len(dynamicDict[0])
        
        rowHeaderString = ','.join(dynamicDict[0])
        rowHeaderString = rowHeaderString.replace("row_amount","amount")        
        now = datetime.now()
        todayDate= now.strftime('%Y-%m-%d %H:%M:%S')
        query = "insert into predicted_data(" +audit_data_key+ conf_key + " user_id, predicted_by,created_datetime,predicted_status,config_uuid,predicted_uuid,file_uuid,original_file_name,company_code) values "
        query += "( " + audit_data_value  + conf_score + " '" + user_id + "','1','" + todayDate + "','1','"+ config_uuid+"','"+ UUID+"','"+ file_uuid +"','"+ original_file_name +"','"+ company_code +"')"
        if not self.SQL_INJECTION_CHECK(query):
            _db = databaseconnection()
            
            _db.execute_non_query(query)

            predicted_id= user_id
            
            if(header_lenth>0):
                for list in dynamicDict[1]:
                    rowHeaderValue=''
                    for stritem in list:
                        rowHeaderValue +=  "'" + stritem.replace("\'","\'\'") + "',"
                    rowHeaderValue = rowHeaderValue[:-1]
                    try:
   
                        query="INSERT INTO predicted_table_data("+ rowHeaderString +",predicted_id,created_datetime,predicted_uuid,config_uuid)VALUES("+rowHeaderValue +",'"+ predicted_id +"','"+ todayDate +"','"+ UUID+"','"+ config_uuid+"')"
                       
                        if not self.SQL_INJECTION_CHECK(query):
                            _db = databaseconnection()
                            try:
                                _db.execute_non_query(query)
                            except Exception as e:
                                print(e)
                               
                        else:
                            return "Miscellaneous Action found" 
                    except Exception as e:
                        print(str(e))

            return "" 
        else:
            return "Miscellaneous Action found"

    def mapping_custom_field_for_report(self,user_id,field_type,config_id):
        fields_name = ""
        objcustom  = customfields()
        results = objcustom.get_fields_for_report(user_id,field_type,config_id)
         
        return results

    def Excel_Data_Templatewise(self, user_id,template_id,from_date,to_date):
        try:

            config_id = template_id #self.get_config_uuid(template_id)       
         
            fields_name = self.mapping_custom_field_for_report(user_id,"S",config_id)
            custom_fields = self.mapping_custom_field_for_report(user_id,"SC",config_id) 

            table_fields_name = self.mapping_custom_field_for_report(user_id,"T",config_id)
            table_custom_fields = self.mapping_custom_field_for_report(user_id,"TC",config_id) 

            
            if(custom_fields != ""):
                fields_name = fields_name[1:] +  custom_fields 
                
            if(table_fields_name != ""):    
                fields_name = fields_name +  table_fields_name 
            
            if(table_custom_fields != ""):
                fields_name = fields_name +  table_custom_fields
 
           
            query = "SELECT original_file_name as 'Main File'," + fields_name + "  from predicted_data WITH (NOLOCK) left join  predicted_table_data WITH (NOLOCK) on predicted_table_data.Predicted_UUID = predicted_data.Predicted_UUID "
            query = query + " where "
             

            if(from_date != "" and to_date != ""):
                start_date = datetime.strptime(from_date ,"%m/%d/%Y").date()
                end_date = datetime.strptime(to_date ,"%m/%d/%Y").date()
                query +=  " ( CONVERT(varchar(10),created_datetime, 23) between '" + datetime.strftime(start_date, '%Y-%m-%d') + "' and '" + datetime.strftime(end_date, '%Y-%m-%d') +"' ) and "
            if(config_id != ""):
                query = query + " audited_data.config_uuid = '" + config_id + "' and " 
            
            query = query + " audited_data.user_id = '" + user_id + "'" 
            
            _db = databaseconnection()
                     
            result = _db.execute_Query(query) 
            query = query.replace("total_amount as","audited_data.total_amount as ")

            df = pd.DataFrame.from_records(result)
             
            return df
        except Exception as e:
            print(str(e))
