from invoiceapp.db_operations.databaseconnection import databaseconnection
from datetime import datetime
from invoiceapp.business_logic.customfields import customfields
from datetime import datetime,timedelta

class users:   
    def __init__(self):
        pass     
    def is_user_exist(emailid):
        query = "SELECT count(1) as recCount FROM auth_user WITH (NOLOCK) where email = '" + str(emailid) +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        
        if(result[0]["recCount"] == 1):
            return True
        else:
            return False
            
    def user_type(user_id):
        query = "SELECT is_local_admin FROM auth_user WITH (NOLOCK) where id = '" + str(user_id) +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        
        if(result[0]["is_local_admin"] == 1):
            return True
        else:
            return False        

    def get_user_list(company_code):
        query = "SELECT user_id, first_name,is_local_admin,last_name,email,username, convert(varchar(10),date_joined,101) as date_joined,is_active,auth.id as id,is_staff,is_superuser ,business_email,organization_name,primary_contact_number,is_online,is_active  FROM auth_user auth WITH (NOLOCK) left join organization_detail org WITH (NOLOCK) on auth.id = org.user_id where auth.company_code = '" +company_code+ "'"
        _db = databaseconnection()
        result = _db.execute_Query(query)  
        print(query)      
        return result

    def update_profile_pic(user_id, file_name):
        query = "update auth_user set profile_img = '" +file_name+ "' where id = " + user_id
        #print(query)
        _db = databaseconnection()
        _db.execute_non_query(query)        
        return ""
    
    def update_organization_pic(user_id, file_name):
        query = "update auth_user set org_img = '" +file_name+ "' where id = " + user_id
        #print(query)
        _db = databaseconnection()
        _db.execute_non_query(query)        
        return ""


    def is_admin_authenticate_user(auth_code,auth_pin):
        query = "SELECT count(1) as recCount FROM auth_user WITH (NOLOCK) where auth_code = '" + str(auth_code) +"' and auth_pin = '" +auth_pin+ "'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        
        if(result[0]["recCount"] == 1):
            query = "update auth_user set is_active = 1 where auth_code = '" + str(auth_code) +"' and auth_pin = '" +auth_pin+ "'"
            _db.execute_non_query(query) 
            return True
        else:
            return False

    def create_new_user(username,password,first_name,last_name,email,company_name,is_staff,profile_img,company_code,contact_email,auth_code,auth_pin,u_encrypt_pass):        
        # print("yessssssssssssss")
        now = datetime.now()
        is_local_admin = '0'
        if is_staff == 'true' or is_staff == '1':
            # print("2222222222222222222222222")
            is_local_admin = '1'

        query = "insert into auth_user (username,password,first_name,last_name,email,company_name,is_staff,is_superuser,is_active,date_joined,profile_img,org_img, company_code,is_local_admin,contact_email,auth_code,auth_pin,u_encrypt_pass,takeatour) OUTPUT INSERTED.id values "
        query += "('" + username + "' ,'" + password + "','" + first_name + "','" + last_name + "','" + email + "','" + company_name + "','0','0','1','" + str(now) + "','" + profile_img + "','logo.png','" + company_code + "','" + is_local_admin + "','" + contact_email + "','" + auth_code + "','" + auth_pin + "','" + u_encrypt_pass + "', '1')"
        _db = databaseconnection()
        # print(query,"Aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        result = _db.execute_Query(query)
        # print(result,"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        return str(result[0]["id"])

    def insert_organization_detail(user_id,business_email,organization_name,primary_contact_number,secondary_contact_number,mailing_address,organization_size,about_organization):        
    
        query = "insert into organization_detail (user_id,business_email,organization_name,primary_contact_number,secondary_contact_number,mailing_address,organization_size,about_organization,schedule_interval,schedule_time,file_shared_location) VALUES "
        query += "('" + user_id + "','','"+organization_name+"','','','','','','daily','11:59','')"
        print(query)
        _db = databaseconnection() 
        _db.execute_non_query(query)     
        return ""

    def get_user_info(user_id):
        query = "SELECT first_name,last_name,is_local_admin,company_code,company_name,email,username,convert(varchar(10),date_joined,101) as date_joined,is_active,id,is_superuser,profile_img ,org_img, takeatour FROM auth_user WITH (NOLOCK) where  id = '" + str(user_id) + "'"
        _db = databaseconnection()
        result = _db.execute_Query(query)        
        return result 

    def get_user_full_info(user_id):
        query = "SELECT user_id, schedule_interval,schedule_time,file_shared_location,first_name,last_name,email,date_joined,is_active,auth.id,is_superuser,profile_img,business_email,organization_name,primary_contact_number,secondary_contact_number,mailing_address,organization_size,about_organization, auth.last_updated as last_updated, takeatour  FROM auth_user auth WITH (NOLOCK) left join organization_detail org WITH (NOLOCK) on auth.id = org.user_id where auth.id = '" + str(user_id)+"'"
        print(query,"ssss")
        _db = databaseconnection()
        result = _db.execute_Query(query)  
        print(result,"@@@")
        return result   
    def update_user_data(query):
        _db = databaseconnection()
        #print(query)
        result = _db.execute_non_query(query)  
        return ""

    def update_user_profile(user_id,business_email,organization_name,primary_contact_number,secondary_contact_number,mailing_address,organization_size,about_organization,schedule_interval,schedule_time,file_shared_location):
        if user_id is None:
            user_id = ''
        if business_email is None:
            business_email = ''
        if organization_name is None:
            organization_name = ''
        if primary_contact_number is None:
            primary_contact_number = ''
        if secondary_contact_number is None:
            secondary_contact_number = ''
        if mailing_address is None:
            mailing_address = ''
        if organization_size is None:
            organization_size = ''
        if about_organization is None:
            about_organization = ''
        if schedule_interval is None:
            schedule_interval = ''
        if schedule_time is None:
            schedule_time = ''
        if file_shared_location is None:
            file_shared_location = ''
        print(organization_size,"iiiii")
        try:
            query = "update organization_detail set business_email = '" +business_email+ "',organization_name = '" +organization_name+ "',primary_contact_number = '" +primary_contact_number+ "',secondary_contact_number = '" +secondary_contact_number+ "',mailing_address = '" +mailing_address+ "',organization_size = '" +organization_size+ "',about_organization = '" +about_organization+ "' ,schedule_time = '" +schedule_time+ "',schedule_interval = '" +schedule_interval+ "',file_shared_location = '" +file_shared_location+ "' where user_id = '" + user_id + "'"
            
            _db = databaseconnection()
            _db.execute_non_query(query)      
            return ""
        except Exception as e:
            print(e)
    
    def get_useraction_list(self,user_id,company_code):
        
        query = "SELECT  u.profile_img,o.business_email,o.organization_name,o.primary_contact_number from auth_user u WITH (NOLOCK)  INNER JOIN organization_detail o WITH (NOLOCK) ON u.id = o.user_id WHERE   u.id = '" + str(user_id) + "' "
        #print(query)
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        print(result)
        #print(result)
        profile_list=["profile_img","business_email","organization_name","primary_contact_number"]

        profile_pic_status=0
        profile_pic_color='danger'
        profile_value=0
        profile_pic_percent = 0
        if(result[0]['profile_img'] != 'demo_img.png'):
             profile_pic_percent=100
             profile_pic_color='success'

        for name in profile_list:
            if(result[0][name]):
                profile_value=profile_value+1

        if(profile_value<2):
            profile_color='danger'
        elif(profile_value==2):
            profile_color='warning'
        elif(profile_value>2):
            profile_color='success'

        query = "SELECT  count(*) as config_list  from form_fields_master WITH (NOLOCK) where company_code = '" + company_code + "'";
        _db = databaseconnection()
        config_list = _db.execute_Query(query)

        if(config_list[0]["config_list"]>0):
            file_config_color='success'
            file_config_percent=100
        else:
            file_config_percent=0
            file_config_color='danger'

        query = "SELECT  count(*) as file_uploaded  from user_invoices WITH (NOLOCK) WHERE   company_code = '" + str(company_code) + "' "
        _db = databaseconnection()
        file_uploaded = _db.execute_Query(query)

        if(file_uploaded[0]["file_uploaded"]>0):
            file_uploaded_color='success'
            file_uploaded_percent=100
        else:
            file_uploaded_percent=0
            file_uploaded_color='danger'


        query = "SELECT  count(*) as predictedCount  from user_invoices WITH (NOLOCK) WHERE status=1 and   company_code = '" + str(company_code) + "' "
        _db = databaseconnection()
        predictedCount = _db.execute_Query(query)

        if(file_uploaded[0]["file_uploaded"]>0 and predictedCount[0]["predictedCount"]== 0 ):
            predictedCount_color='success'
            predictedCount_percent=100
        else:
            predictedCount_percent=0
            predictedCount_color='danger'


        query = "SELECT  count(*) as auditedCountRow  from audited_data WITH (NOLOCK) WHERE   company_code = '" + str(company_code) + "' "
        _db = databaseconnection()
        auditedCountRow = _db.execute_Query(query)

        query = "SELECT  count(*) as auditedCount  from predicted_data WITH (NOLOCK) WHERE predicted_status=1 and   company_code = '" + str(company_code) + "' "
        _db = databaseconnection()
        auditedCount = _db.execute_Query(query)

        if(file_uploaded[0]["file_uploaded"]>0 and auditedCount[0]["auditedCount"] == 0 and auditedCountRow[0]["auditedCountRow"] >0 ):
            auditedCount_color='success'
            auditedCount_percent=100
        else:
            auditedCount_percent=0
            auditedCount_color='danger'


        
        profile_dict= { "profile_color": profile_color, "profile_percent" : profile_value*25 }
        profile_pic= { "profile_pic_percent": profile_pic_percent, "profile_pic_color": profile_pic_color  }
        config_dict = { "file_config_percent": file_config_percent, "file_config_color": file_config_color } 
        file_uploaded= { "file_uploaded_percent": file_uploaded_percent, "file_uploaded_color": file_uploaded_color  }
        predictIdp= { "predictedCount_percent": predictedCount_percent, "predictedCount_color": predictedCount_color  }
        auditedData= { "auditedCount_percent": auditedCount_percent, "auditedCount_color": auditedCount_color  }
 

        final_dict={ "profile_dict": profile_dict ,"profile_pic":profile_pic, "file_uploaded" : file_uploaded, "predictIdp" : predictIdp, "auditedData" : auditedData, "config_dict": config_dict }

        return final_dict
    
    def get_configuration_list(self, user_id, company_code):
        objcustom  = customfields()
        query = "SELECT config_name, id, config_uuid,is_active from form_fields_master WITH (NOLOCK) where company_code = '" + company_code + "'"; 
        _db = databaseconnection()
        config_list = _db.execute_Query(query)
        dict_config = []
        
        for config in config_list:
            
            fieldsConfiguration = objcustom.get_custom_fields_by_uuid(config["config_uuid"],user_id,company_code)
            dict_config.append({"config_uuid" : config["config_uuid"], "config_name" : config["config_name"], "config_status" : config["is_active"] ,"config_data" : fieldsConfiguration})
        # print(dict_config,"444444")
       
        return dict_config

    def accuracy_data(user_id):

        accuracy_dict= []
        _db = databaseconnection()
        D=9
        fromDate_datetime = datetime.now() - timedelta(days=D) 
        fromDate= fromDate_datetime.date()
        
        toDate_datetime = datetime.now()+ timedelta(days=1)
        toDate= toDate_datetime.date()
        dict_predict = []

        predict_query = "Select  CEILING((AVG(CAST(accuracy_percent AS DECIMAL(10, 4))))) as accuracy ,CONVERT(VARCHAR(10), accuracy_date , 23) as accuracy_date  from accuracy_info WITH (NOLOCK) where  user_id = '" + user_id + "'  AND  CONVERT(varchar(10), cast(accuracy_date as date),101) between CONVERT(varchar(10),cast('" + str(fromDate) +"' as date) ,101) and CONVERT(varchar(10),cast('" + str(toDate) +"' as date), 101) group by user_id , accuracy_date"
        predict_list = _db.execute_Query(predict_query)
        
        audit_list = predict_list
        
        dict_audit = [] 
        dict_date = []
        list_accuracyinfo = []
        delta = toDate_datetime - fromDate_datetime

        deltadays= delta.days-1

        for i in range(deltadays + 1):
            last_date=''
            last_date=fromDate_datetime + timedelta(days=i)
            dict_date.append(last_date.date().strftime('%Y-%m-%d'))

       
        for dt in predict_list:
            list_accuracyinfo.append(dt.get("accuracy_date") + "$$" + str(dt.get("accuracy")))
            
        #print(list_accuracyinfo)
        
        dicts = {}
        
        for i in list_accuracyinfo:
            items = i.split("$$")
            key = str(items[0])
            dicts[key] = (items[1])

        
        month_name=''
        predicted_count_string=''
        audited_count_string=''

        for in_date in dict_date:
            if str(in_date) in dicts:
                predicted_count_string = predicted_count_string + dicts[str(in_date)]+ ", "
                audited_count_string = audited_count_string + dicts[str(in_date)] + ", "
                month_name = month_name +   datetime.strptime(in_date, '%Y-%m-%d').strftime('%d %B') + ", " 
            else: 
                month_name = month_name +   datetime.strptime(in_date, '%Y-%m-%d').strftime('%d %B') + ", " 
                predicted_count_string = predicted_count_string + "0, "
                audited_count_string = audited_count_string + "0, "

 
        accuracy_dict.append({"date_string" : month_name.strip(', '), "predicted_count" : predicted_count_string.strip(', ') ,"audited_count" : audited_count_string.strip(', ') })
        return accuracy_dict

    def insert_feedback(user_id,rate,feedback):

        now = datetime.now()
        query = "insert into user_feedback(user_id,rate,feedback,datetime,status) VALUES "
        query += "('" + user_id + "','" + rate + "','" + feedback + "','" + str(now) + "','1')"
        _db = databaseconnection() 
        _db.execute_non_query(query)     
        return ""
        
    def process_vs_audited_trend(user_id,company_code):
        _db = databaseconnection()
        pvsa_trend_dict= []

        D=9
        fromDate_datetime = datetime.now() - timedelta(days=D) 
        fromDate= fromDate_datetime.date()
        
        toDate_datetime = datetime.now()+ timedelta(days=1)
        toDate= toDate_datetime.date()
        dict_predict = []

        predict_query = "SELECT predicted_id, CONVERT(VARCHAR(10), created_datetime , 111)  as created_date from predicted_data WITH (NOLOCK) where company_code = '" + company_code + "'  AND  CONVERT(varchar(10), cast(created_datetime as date),101) between CONVERT(varchar(10),cast('" + str(fromDate) +"' as date) ,101) and CONVERT(varchar(10),cast('" + str(toDate) +"' as date), 101) "
        predict_list = _db.execute_Query(predict_query)
        
        

        audit_query = "SELECT audited_id,CONVERT(VARCHAR(10), audited_datetime , 111)  as  audited_date from audited_data WITH (NOLOCK) where company_code = '" + company_code + "'  AND  CONVERT(varchar(10), cast(audited_datetime as date),101) between CONVERT(varchar(10),cast('" + str(fromDate) +"' as date) ,101) and CONVERT(varchar(10),cast('" + str(toDate) +"' as date), 101) "
        audit_list = _db.execute_Query(audit_query)

    
        dict_audit = []
        

        dict_date = []
        delta = toDate_datetime - fromDate_datetime

        deltadays= delta.days-1

        for i in range(deltadays + 1):
            last_date=''
            last_date=fromDate_datetime + timedelta(days=i)
            dict_date.append(last_date.date().strftime('%Y-%m-%d'))

        month_name=''
        predicted_count_string=''
        audited_count_string=''

        for dt in dict_date:
            predicted_count=0
            audited_count=0
            
            for qt in predict_list:
                if(dt == qt['created_date']):
                    predicted_count=predicted_count+1
            for qt in audit_list:
                if(dt == qt['audited_date']):
                    audited_count=audited_count+1
            
            month_name = month_name +   datetime.strptime(dt, '%Y-%m-%d').strftime('%d %B') + ", " 
            predicted_count_string = predicted_count_string + str(predicted_count) + ", "
            audited_count_string = audited_count_string + str(audited_count) + ", "
        pvsa_trend_dict.append({"date_string" : month_name.strip(', '), "predicted_count" : predicted_count_string.strip(', ') ,"audited_count" : audited_count_string.strip(', ') })

        
        return pvsa_trend_dict
         
    def get_process_log(company_code):
            query = "SELECT * FROM process_log WHERE company_code = '" +company_code+ "' ORDER BY process_id DESC"
            _db = databaseconnection()
            result = _db.execute_Query(query)  
            #print(result)      
            return result 

    def get_supplier(company_code):
            query = "SELECT * FROM stp_supplier WHERE company_code = '" +company_code+ "'"
            _db = databaseconnection()
            result = _db.execute_Query(query)  
            #print(result)      
            return result  

    def addsupplier(supplier_id,supplier_name,supplier_status,company_code):        
            now = datetime.now()
            if supplier_id:
                query = "UPDATE  stp_supplier set supplier_name='" + supplier_name + "',supplier_status='" + supplier_status + "',update_date='" + str(now) + "' where supplier_id='" + supplier_id + "'"
            else:
                query = "insert into stp_supplier (supplier_name,supplier_status,add_date,update_date,supplier_desc,company_code) values"
                query += "('" + supplier_name + "' ,'" + supplier_status + "','" + str(now) + "','" + str(now) + "','','" + company_code + "')"
            _db = databaseconnection()
            #print(query)
            result = _db.execute_Query(query)
            return str(result[0]["id"])