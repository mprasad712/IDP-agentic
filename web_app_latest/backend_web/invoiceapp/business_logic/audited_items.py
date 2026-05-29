from invoiceapp.db_operations.databaseconnection import databaseconnection
from datetime import datetime
from invoiceapp.business_logic.customfields import customfields


class audited_items:   
    def __init__(self):
        pass     

    def is_item_exist(predicted_uuid):
        query = "SELECT count(1) as rec_count  FROM audited_data WITH (NOLOCK) where  UUID = '" + str(predicted_uuid) +"'"  
        _db = databaseconnection()
        #print(query)
        result = _db.execute_Query(query)
        if(result[0]["rec_count"] == 0):
            return False
        else:
            return True 

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
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        # print(result,"************************")
         
        return result[0]["config_uuid"]

    def get_standard_data(self,rec_id, file_id,user_id,company_code):
        config_id = self.get_config_uuid(rec_id) 
        fields_name = ""
        standard_fields= self.mapping_fields(user_id,"S",config_id,company_code)
        custom_standard = self.mapping_fields(user_id,"SC",config_id,company_code)
        if custom_standard != "" and standard_fields != "":
            fields_name = standard_fields + "," + self.mapping_fields(user_id,"SC",config_id,company_code)
        elif custom_standard == "" and standard_fields != "":
            fields_name = standard_fields
        elif custom_standard != "" and standard_fields == "":
            fields_name = custom_standard

        query = "SELECT " + fields_name + " , UUID from audited_data WITH (NOLOCK) where UUID = '" + rec_id + "'"; 
        print("$$$$$$$$$$",query)
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result

    def get_data(customer_code,user_id):
        #query = "SELECT fields_name,field_key,field_type from form_fields where customer_code = '" + customer_code + "'"; 
        #_db = databaseconnection()
        #result = _db.execute_Query(query)
        auditedData  = [{"id" : "1001","invoice_name":"90000","audited_datetime":"10/20/20 10:10:10 AM","status": "Pending","audited_by": ""},{"id" : "1001","invoice_name":"90000","audited_datetime":"10/20/20 10:10:10 AM","status": "Pending","audited_by": ""},{"id" : "1001","invoice_name":"90000","audited_datetime":"10/20/20 10:10:10 AM","status": "Pending","audited_by": ""},{"id" : "1001","invoice_name":"90000","audited_datetime":"10/20/20 10:10:10 AM","status": "Pending","audited_by": ""}]  
        return auditedData
    
    def get_all_standard_data(user_id,company_code):
        query = "SELECT original_file_name,UUID,user_id,file_name,po_number,invoice_number, invoice_date,convert(varchar, audited_datetime, 9) as audited_datetime,audited_status, auth_user.first_name as 'first_name' , auth_user.last_name as 'last_name'  from audited_data audit WITH (NOLOCK) inner join auth_user WITH (NOLOCK) on audit.user_id = auth_user.id where audit.company_code = '" + company_code + "' order by audited_datetime DESC"; 
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result

    def get_audit_info(customer_code,user_id):
        pass

        # Get fields name from custom fields customfields = get_fields() 
        # fields_name = customfields.get_custom_fields(user_id)
        # result = {"data" : customfields}

    def update_audit_status(predicted_uuid,status):
        UpdateQuery="UPDATE predicted_data SET predicted_status='"+ status +"' WHERE predicted_uuid='" +predicted_uuid+ "'"
        _db = databaseconnection()
        _db.execute_non_query(UpdateQuery)

    def roll_back_audit_item(predicted_uuid):
        delete_query = "Delete from audited_data where UUID = '" + predicted_uuid + "'"
        delete_query += "; Delete from audited_table_data where UUID = '" + predicted_uuid + "'"
        _db = databaseconnection()
        _db.execute_non_query(delete_query)

    def file_audit_submit(user_id,StandardFieldList,rowHeaderList,rowColumnList,predicted_uuid,config_uuid,file_uuid,company_code):
        try:
            print(rowColumnList,"+++")
            print(StandardFieldList,"##$$$")
            print("File audit submit")            
            audit_data_key=''
            audit_data_value=''
            for key, value in StandardFieldList.items():
                if key != 'invoiceID':
                    print("MMMMMM")
                    audit_data_key += key +',' 
                    val = value.replace("null","") 
                    val = val.replace("None","") 
                    audit_data_value +=  "'" + val.replace("\'", "\'\'") + "' , "
                if key == 'invoiceID':
                    invoiceID = value
                    
            header_lenth = len(rowHeaderList)
            rowHeaderString = ','.join(rowHeaderList)        
            now = datetime.now()
            todayDate= now.strftime('%Y-%m-%d %H:%M:%S')
            query = "insert into audited_data(" +audit_data_key+ " audited_datetime,audited_status,audited_by,UUID,user_id,config_uuid,file_uuid,company_code) values "
            query += "( " + audit_data_value + " '" + todayDate + "','3'," +user_id+ ",'" + predicted_uuid + "','" + user_id + "','" + config_uuid + "','" + file_uuid + "','" + company_code + "')"
            # print(query)
            _db = databaseconnection()
            _db.execute_non_query(query)
            rowTableValue=''
            rowTableList=[]
            if(header_lenth>0):
                tableData = rowColumnList
                for list in tableData:
                    print(list,"+++")
                    # rowTableValue=''
                    # Iterate over all key-value pairs
                    for key, value in list.items():
                        print(value,"========")
                        # value += "'" + value.replace("\'", "\'\'") + "',"
                        rowTableList.append(value)
                    
                    print(rowTableList)
                    rowTableValue=''
                    for str in rowTableList:
                        rowTableValue +=  "'" + str.replace("\'", "\'\'") + "',"
                        print(rowTableValue,"++++++++")
                    rowTableValue = rowTableValue[:-1]
                    
                    query="INSERT INTO audited_table_data(audited_id,"+ rowHeaderString +",created_datetime,UUID,config_uuid)VALUES("+predicted_uuid +","+rowTableValue +","+ todayDate +"," + predicted_uuid + "," + config_uuid + ")"
                    
                    _db = databaseconnection()
                    
                    _db.execute_non_query(query)
        except Exception as e:
            raise(e)
       
