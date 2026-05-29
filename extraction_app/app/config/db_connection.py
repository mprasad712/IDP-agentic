import json
from datetime import datetime
import pprint, traceback
import uuid
import os

from collections import OrderedDict

import pyodbc

DATABASE_NAME = os.environ.get('DB_NAME','db_idp')
DATABASE_USER = os.environ.get('DB_USER','SA')
DATABASE_PASSWORD = os.environ.get('DB_PASSWORD','Ocrdb@12#')
DATABASE_HOST = os.environ.get('DB_HOST','127.0.0.1')
DATABASE_PORT = os.environ.get('DB_PORT','1433')



def connect_db():
    try:

        mydb = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};' +

                              'Server={};'.format(DATABASE_HOST) +

                              'port={};'.format(DATABASE_PORT) +

                              'Database={};'.format(DATABASE_NAME) +

                              'uid={};'.format(DATABASE_USER) +

                              'pwd={};'.format(DATABASE_PASSWORD) +

                              'autocommit=True;'

                              )
        print("SUCCESSSS")
        
        return mydb
    except:
        print("@@@###############")
        traceback.print_exc()




def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"

    columns = [col[0]

               for col in cursor.description]

    return [

        OrderedDict(zip(columns, row))

        for row in cursor.fetchall()

        ]


def execute_non_query(query, mydb):
    try:
        print(type(query),"+++*****")
        mycursor = mydb.cursor()
        mycursor.execute(query)
        mycursor.commit()
        return 'success'
    except:
        print("Error in db")
        traceback.print_exc()


def execute_query(mydb,query):
    myresult = []
    #mydb = connect_db()
    mycursor = mydb.cursor()

    mycursor.execute(query)

    myresult = dictfetchall(mycursor)

    return myresult





def execute_query_v2(mydb, query):
    try:
        cursor=mydb.cursor()
        cursor.execute(query)
        db_out = dictfetchall(cursor)
        return db_out
    except:

        traceback.print_exc()
        return db_out
def fetch_client_email_data_without_Userid(mydb):
    # user_id = ""
    config_list = []
    out_json = {}
    # query = "SELECT * from mail_configuration where userid = '" + user_id + "'";
    query = "SELECT f.config_name, f.id as config_id, m.* from mail_configuration m left join form_fields_master as f on  \
            m.user_id = f.user_id order by config_id desc";
    out = execute_query_v2(mydb,query)
    if len(out)==0:
        out_json = {"success" : "0", "config_list" : "", "user_id" : "","message" : "Could not fetch Client mail Configuration !!", \
                "company_code": "", "mail_id" : "", "subject": "", "from_email" : "", "smtp" : "", "username" : "", "password" : "", \
                "port" : ""}
        return out_json
    else:
        return out



def get_fields_Names(dbList):
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
def get_standard_fields_mapping(user_id,ftype,config_uuid,company_code):
        
        query = "SELECT fields_name,field_key,field_type,field_sequence,mapped_field from form_fields_mapping WITH (NOLOCK)  where field_type = '" + ftype + "' and company_code = '" + str(company_code) + "' and config_uuid =  '" + str(config_uuid) + "' order by field_sequence"
         
        mydb = connect_db()
        result = execute_query(mydb,query) 
        output = get_fields_Names(result) 
        return output

def mapping_fields(user_id,field_type,config_id,company_code):
        fields_name = ""

        results = get_standard_fields_mapping(user_id,field_type,config_id,company_code)
        if(field_type == "S"):
            fields_name = results["standard_list"]
        elif(field_type == "SC"):
            fields_name = results["standard_custom_list"]
        elif(field_type == "T"):
            fields_name = results["table_list"]
        elif(field_type == "TC"):
            fields_name =  results["table_custom_list"]

        return fields_name

def get_standard_data(uuid,rec_id,user_id,company_code):

        #config_id = self.get_config_uuid(rec_id)
        config_id = rec_id 
        
         
        fields_name = mapping_fields(user_id,"S",config_id,company_code)
        custom_fields = mapping_fields(user_id,"SC",config_id,company_code) 
         
        if(custom_fields != ""):
            fields_name = fields_name + "," + custom_fields
         
        
        fields_conf_score = fields_name.replace(",",",conf_")
        fields_conf_score = fields_conf_score.replace("file_name","conf_file_name")
        query = "SELECT original_file_name,user_id,company_code,config_uuid,predicted_uuid," + fields_name + ", " + fields_conf_score + "  from predicted_data WITH (NOLOCK) where predicted_uuid = '" + uuid + "'"; 

        mydb = connect_db()
        result = execute_query(mydb,query)
         
        return result
    
def get_table_data(uuid,rec_id,user_id,company_code):
        #config_id = self.get_config_uuid(rec_id)
        config_id = rec_id
        
        
        fields_name = mapping_fields(user_id,"T",config_id,company_code)
        custom_fields = mapping_fields(user_id,"TC",config_id,company_code)
         
        if mapping_fields(user_id,"TC",config_id,company_code) != "":
            fields_name = fields_name + ","+ mapping_fields(user_id,"TC",config_id,company_code)
        else:
            fields_name = fields_name 
        
        fields_name = fields_name.strip(",")

        if(fields_name != ""):
            query = "SELECT " + fields_name + "  from predicted_table_data WITH (NOLOCK) where predicted_uuid = '" + uuid + "'"; 

            mydb = connect_db()
            result = execute_query(mydb,query)
            return result
        else:
            return ''
def get_display_list(dbList):
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


def get_custom_fields_by_uuid(config_uuid,company_code):
    query = "SELECT fields_name,field_key,field_type,field_sequence,mapped_field from form_fields_mapping WITH (NOLOCK) where config_uuid = '" + str(config_uuid) + "' and company_code = '"+ company_code+"' order by field_sequence";
    mydb = connect_db()
    result = execute_query(mydb,query)
    output = get_display_list(result)
    return output

def save_process_log(file_name, todayDate, company_code, file_uuid, case_id, doc_type, is_duplicate, country_code):
    query = "Insert into process_log (file_name,start_date,end_date,log_status,log_message,company_code,file_uuid,case_id,doc_type,is_duplicate, country_code) values "
    query += "('" + file_name + "' ,'" + todayDate + "','','2','','" + company_code + "','" + file_uuid + "','" + case_id + "','" + doc_type + "','" + is_duplicate + "','" + country_code + "')"

    
    try:
        mydb = connect_db()
        execute_non_query(query,mydb)
    except Exception as e:
        error_log(file_name,str(e))
        print("DB error")
        traceback.print_exc()


def save_user_invoice(user_id,config_id,file_name,company_code,file_uuid):
    file_name= file_name.replace("\'", "\'\'")
    original_file_name =  file_name 
    status = '2'
    invoice_uid = file_uuid
    now = datetime.now()
    todayDate = now.strftime('%Y-%m-%d %H:%M:%S')
    query = "Insert into user_invoices (file_name,user_id,updated_datetime,status,invoice_uid,config_id,run_by,original_file_name,company_code) values "
    query += "('" + file_name + "' ,'" + user_id + "','" + todayDate + "','" + status + "','" + invoice_uid + "','" + config_id + "','automate','" + original_file_name + "', '" + company_code + "')"

    try:
        mydb = connect_db()
        execute_non_query(query,mydb)
    except Exception as e:
        error_log(file_name,str(e))
        print("DB error")
        traceback.print_exc()


def save_idp_output(user_id, config_uuid, staticDict, dynamicDict, UUID, file_uuid,company_code):
    try:
        print("ENTERRRRR@@@@@@@@@@@")
        audit_data_key = ''
        audit_data_value = ''
        conf_score = ''
        conf_key = ''
        mydb = connect_db()
        for key, value in staticDict.items():
            audit_data_key += key + ','
            conf_key += "conf_" + key + ','
            if (key == "file_name"):
                replaced_val = value[0].replace("\'", "\'\'")
                audit_data_value += "'" + replaced_val.replace("null", "")  + "' , "
                original_file_name =  replaced_val
                
            else:
                replaced_val = value[0].replace("\'", "\'\'")
                audit_data_value += "'" + replaced_val.replace("null", "") + "' , "
            try:
                conf_value = str(value[1]).replace("NA", "")
                conf_score += "'" + conf_value + "' , "
            except Exception as e:
                print(e)
        print("########ENTERRRRR@@@@@@@@@@@", dynamicDict)
        header_lenth = len(dynamicDict[0])
        rowHeaderString = ','.join(dynamicDict[0])
        rowHeaderString = rowHeaderString.replace("row_amount", "amount")
    
        now = datetime.now()
        # print("@#@#@#@#@#@#",supplier_name)
        # supplier_stp = get_supplier(supplier_name, company_code)
        todayDate = now.strftime('%Y-%m-%d %H:%M:%S')
        
        #return 0 
    
        
        
            # alertMail(staticDict['file_name'][0],"Audit document alert from PO to SO")
        query = "insert into predicted_data(" + audit_data_key + conf_key + " user_id, predicted_by,created_datetime,predicted_status,config_uuid,predicted_uuid,file_uuid,original_file_name, company_code) values "
        query += "( " + audit_data_value + conf_score + " '" + user_id + "','"+ user_id +"','" + todayDate + "','1','" + config_uuid + "','" + UUID + "','" + file_uuid + "','" + original_file_name + "','" + company_code + "')"
    
        try:
            print("query", query)
            execute_non_query(query,mydb)
        except Exception as e:
            error_log("Query Error",str(e))
            print("DB error")
            traceback.print_exc()
    
        predicted_id = user_id
        tbl_query = ""
        if (header_lenth > 0):
    
            for list in dynamicDict[1]:
    
                rowHeaderValue = ''
    
                for stritem in list:
                    # stritem = str(stritem)
                    rowHeaderValue += "'" + stritem.replace("\'", "\'\'") + "',"
    
                rowHeaderValue = rowHeaderValue[:-1]
    
                query = "INSERT INTO predicted_table_data(" + rowHeaderString + ",predicted_id,created_datetime,predicted_uuid,config_uuid)VALUES(" + rowHeaderValue + ",'" + predicted_id + "','" + todayDate + "','" + UUID + "','" + config_uuid + "')"
                print("table data",query)
                tbl_query = tbl_query + "; "+ query
            if len(tbl_query)>0:
                execute_non_query(tbl_query, mydb)
    
            now = datetime.now()
            todayDate = now.strftime('%Y-%m-%d %H:%M:%S')
            query = "UPDATE process_log set end_date='"+todayDate+"', log_status='3'  where file_uuid='"+file_uuid+"'"
            try:
                execute_non_query(query,mydb)
            except:
                print("DB error")
                traceback.print_exc()
    
        try:
            query = "update user_invoices set status=3 where invoice_uid='"+file_uuid+"'"
            execute_non_query(query, mydb)
        except:
            print("DB error : user_invoices")
            traceback.print_exc()
        # clear_nohup(nohup_path)
        return ""
    except:
        traceback.print_exc()
        pass

def mapdb_key(business_rule_db_dict, config_uuid, company_code, user_id, case_id, doc_type, country_code):
    try:
        standarddict = get_custom_fields_by_uuid(config_uuid,company_code)
        
        standard_dict = {item['fields_name'].strip().replace(" ", "_"): item['mapped_field'] for item in standarddict["standard_list"]}
        custom_standard_dict = {item['fields_name'].strip().replace(" ", "_"): item['mapped_field'] for item in standarddict["standard_custom_list"]}
        combined_standard_list = {**standard_dict, **custom_standard_dict}
    
    
        table_dict = {item['fields_name'].strip().replace(" ", "_"): item['mapped_field'] for item in standarddict["table_list"]}
        custom_table_dict = {item['fields_name'].strip().replace(" ", "_"): item['mapped_field'] for item in standarddict["table_custom_list"]}
        combined_table_list = {**table_dict, **custom_table_dict}
    
    
        standard_data_maped  = {
        combined_standard_list.get(field_name): value
        for field_name, value in business_rule_db_dict["static"].items()
        if combined_standard_list.get(field_name)  
        }
    
        dynamic_data_maped = [combined_table_list.get(head) for head in business_rule_db_dict["dynamic"][0]]
    
        business_rule_db_dict["static"] = standard_data_maped
        business_rule_db_dict["dynamic"][0] = dynamic_data_maped
    
        #databse insertion
        #user_id = '20359'
        now = datetime.now()
        todayDate = now.strftime('%Y-%m-%d %H:%M:%S')
        is_duplicate = '0'
        file_uuid =  str(uuid.uuid4().hex[:8])
        file_name = business_rule_db_dict["static"]["file_name"][0]
        save_process_log(file_name, todayDate, company_code, file_uuid, case_id, doc_type, is_duplicate, country_code)
        save_user_invoice(user_id,config_uuid,file_name,company_code,file_uuid)
           
        save_idp_output(user_id, config_uuid, business_rule_db_dict["static"],  business_rule_db_dict["dynamic"], file_uuid, file_uuid,company_code)
    except:
        traceback.print_exc()
        pass
    
    # return business_rule_prev_dict


def map_db_keys(business_rule_db_dict, config_uuid, company_code):
    try:
        standarddict = get_custom_fields_by_uuid(config_uuid,company_code)
        
        standard_dict = {item['fields_name'].strip().replace(" ", "_").lower(): item['mapped_field'] for item in standarddict["standard_list"]}
        custom_standard_dict = {item['fields_name'].strip().replace(" ", "_").lower(): item['mapped_field'] for item in standarddict["standard_custom_list"]}
        combined_standard_list = {**standard_dict, **custom_standard_dict}
    
    
        table_dict = {item['fields_name'].strip().replace(" ", "_").lower(): item['mapped_field'] for item in standarddict["table_list"]}
        custom_table_dict = {item['fields_name'].strip().replace(" ", "_").lower(): item['mapped_field'] for item in standarddict["table_custom_list"]}
        combined_table_list = {**table_dict, **custom_table_dict}
    
    
        standard_data_maped  = {
        combined_standard_list.get(field_name): value
        for field_name, value in business_rule_db_dict["static"].items()
        if combined_standard_list.get(field_name)  
        }
    
        dynamic_data_maped = [combined_table_list.get(head) for head in business_rule_db_dict["dynamic"][0]]
    
        business_rule_db_dict["static"] = standard_data_maped
        business_rule_db_dict["dynamic"][0] = dynamic_data_maped
    except:
        traceback.print_exc()
        pass
    
    return business_rule_db_dict


def insert_file(file_name,user_id,status,invoice_uid,config_id,company_code,todayDate):  
        query = "Insert into user_invoices (original_file_name,file_name,user_id,updated_datetime,status,invoice_uid,config_id,run_by,company_code) values "
        query += "('" + file_name + "' ,'" + file_name + "' ,'" + user_id + "','" + todayDate + "','"+ status+"','"+ invoice_uid+"','"+ config_id+"','manual','"+ company_code+"')"
        print(query,"@@####")
        try:
            mydb = connect_db()
            print(mydb,"======")
            result = execute_non_query(query, mydb) 
        except:
            traceback.print_exc()
        return result

def updated_by_UUID(invoice_uuid,status):
        query = "Update user_invoices set status = '"+status+"' where invoice_uid = '" + invoice_uuid + "'"          
        mydb = connect_db()
        result = execute_non_query(query, mydb)    
        return ""


def updated_by_UUID(invoice_uuid,status):
        query = "Update process_log set status = '"+status+"' where invoice_uid = '" + invoice_uuid + "'"          
        mydb = connect_db()
        result = execute_non_query(query, mydb)    
        return ""




