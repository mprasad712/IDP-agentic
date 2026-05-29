from invoiceapp.db_operations.databaseconnection import databaseconnection
from datetime import datetime
from invoiceapp.business_logic.customfields import customfields



class AgenticItems:   
    def __init__(self):
        pass     

    def get_current_date_time(self):
        now = datetime.now()
        formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_date_time
        
    def save_agent_data(self, user_id, company_code, agent_name, agentic_data):  # Corrected spelling inside method
        currentDateTime = self.get_current_date_time()
        query = ("INSERT INTO agent_store "
                 "(user_id, company_code, agent_name, agent_data, created_datetime) VALUES "
                 "('{}', '{}', '{}', '{}', '{}')").format(user_id, company_code, agent_name, agentic_data, currentDateTime)
        _db = databaseconnection()
        result = _db.execute_non_query(query) 
        return result

    def get_agentic_data(self, user_id, company_code, agent_name):  # Adjusted to match usage
        query = "SELECT agent_data FROM agent_store WHERE agent_name = '{}'".format(agent_name)
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result

    def get_all_agentic_data(self, user_id, company_code):  # Adjusted to match usage
        query = "SELECT agent_data FROM agent_store WHERE user_id ='" + str(user_id) +"' and company_code = '" + str(company_code) +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result

    def is_project_exist(self,company_code,agent_name):
        query = "SELECT count(1) as recCount FROM agent_store WITH (NOLOCK) where company_code = '" + str(company_code) +"' and agent_name = '" + agent_name + "'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        if(result[0]["recCount"] >= 1):
            return True
        else:
            return False 

    def get_project_name(self, user_id, company_code):
        query = "SELECT agent_name, id FROM agent_store WITH (NOLOCK) where company_code = '" + str(company_code) +"' and user_id = '" + str(user_id) +"'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        print(result,"$$$%%%")
        return result

    def delete_project(self, user_id, company_code, agent_name):
        query = "DELETE FROM agent_store WHERE company_code = '" + str(company_code) +"' and user_id = '" + str(user_id) +"' and agent_name = '" + str(agent_name) +"'" 
        _db = databaseconnection()
        result = _db.execute_non_query(query) 
        return result

    def update_project(self, user_id, company_code, new_agent_data, agent_name):
        query = "UPDATE agent_store SET agent_data = '" + str(new_agent_data) + "' WHERE company_code = '" + str(company_code) + "' AND user_id = '" + str(user_id) + "' AND agent_name = '" + str(agent_name) + "'"
        _db = databaseconnection()
        result = _db.execute_non_query(query) 
        return result

    def update_running_status(self, user_id, company_code, agent_name, running_status):
        query = "UPDATE agent_store SET running_status = '" + running_status + "' WHERE company_code = '" + str(company_code) + "' AND user_id = '" + str(user_id) + "' AND agent_name = '" + str(agent_name) + "'"
        _db = databaseconnection()
        result = _db.execute_non_query(query) 
        return result

    def get_running_status(self, user_id, company_code, agent_name):
        query = "SELECT running_status FROM agent_store WHERE company_code = '" + str(company_code) + "' AND user_id = '" + str(user_id) + "' AND agent_name = '" + str(agent_name) + "'"
        _db = databaseconnection()
        result = _db.execute_Query(query) 
        return result