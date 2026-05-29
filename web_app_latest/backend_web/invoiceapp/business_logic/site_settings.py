from invoiceapp.db_operations.databaseconnection import databaseconnection
 

class site_settings:   
    def __init__(self):
        pass 

    def get_default_settings():
        query = "SELECT * from  admin_site_config_default WITH (NOLOCK)"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result
         
    def is_config_exist(user_id,setting_id):
        query = "SELECT count(1) as recCount FROM admin_site_config_user WITH (NOLOCK) where  user_id = '" + str(user_id) +"' and setting_id = '" + str(setting_id)+ "'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        print(result[0]["recCount"]) 
        if(result[0]["recCount"] == 1):
            return True
        else:
            return False

    def insert_config_setting(user_id,setting_id,setting_value):
        query = "Insert into  admin_site_config_user(setting_id,user_id,setting_value) values('" + setting_id + "' , '" + user_id + "' , '" + setting_value+ "')"
        print(query)
        _db = databaseconnection()
        _db.execute_non_query(query)

    def update_config_setting(user_id,setting_id,setting_value):
        query = "UPDATE admin_site_config_user set setting_value = '" + setting_value + "' where user_id = '" + user_id+ "' and setting_id = '" + setting_id + "'"
        print(query)
        _db = databaseconnection()
        _db.execute_non_query(query)
         
    
    def get_configuration_list(user_id,company_code):       
        query = "SELECT user_id,setting_id,acu.setting_value,acd.setting_name,display_name from admin_site_config_default acd WITH (NOLOCK) "
        query = query + " inner join admin_site_config_user acu WITH (NOLOCK) on acu.setting_id = acd.id  where acd.company_code = '" + company_code + "'"    
        print(query,"+++++++")
        _db = databaseconnection()
        config_list = _db.execute_Query(query)
        return config_list
 

         
     