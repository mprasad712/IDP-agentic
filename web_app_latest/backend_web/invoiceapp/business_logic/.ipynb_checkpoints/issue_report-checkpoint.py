from invoiceapp.db_operations.databaseconnection import databaseconnection
from datetime import datetime

class issue_report:   
    def __init__(self):
        pass 
    def SQL_INJECTION_CHECK(self,query):
        restricted_list = ["Drop","Alter","truncate","1=1"]
         
        res = [ele for ele in restricted_list if(ele.lower() in query.lower())]        
        if(len(res) > 0):
            is_invalid = True
        else:
            is_invalid = False
        return is_invalid

    def insert_issue_report(self,user_id,subject,discription):
        now = datetime.now()
        todayDate= now.strftime('%Y-%m-%d %H:%M:%S')
        query = "Insert into  issue_reported(user_id,subject,discription,updated_datetime,is_active) values('" + user_id + "' , '" + subject + "' , '" + discription+ "', '" + todayDate+ "','1')"
        if not self.SQL_INJECTION_CHECK(query):
            _db = databaseconnection()
            _db.execute_non_query(query)
            return ""
        else:
            return "Miscellaneous Action found"

 

         
     