def create_database():
    return "CREATE DATABASE db_idp_ips"

def create_tables():
    query = "CREATE TABLE form_fields_mapping ( id int NOT NULL  IDENTITY(1, 1),  user_id int, field_sequence int, fields_name varchar(255), field_key varchar(255), field_type varchar(20), mapped_field varchar(20), is_active int, updated_datetime datetime, PRIMARY KEY (id) );"
    return query

def create_tables():
    query = "CREATE TABLE form_fields_master ( id int NOT NULL  IDENTITY(1, 1),  user_id int, config_name nvarchar(255), config_uuid varchar(255) ,  is_active int , is_deleted int);"

def create_tables():
    query = "CREATE TABLE issue_reported ( id int NOT NULL  IDENTITY(1, 1),  user_id int, subject nvarchar(255), discription varchar(1000) ,  is_active int , updated_datetime datetime, PRIMARY KEY (id) "

def Insert_form_fields():
    query = "INSERT INTO form_fields_mapping values(1001,'Invoice Number'','invoice_number'','ps',1,'')"
    return query
def create_business_logic_tables():
    query = "CREATE TABLE user_business_logic ( id int NOT NULL  IDENTITY(1, 1), user_id int, config_uuid varchar(200), business_logic varchar(500), validation_type varchar(20), is_active int, PRIMARY KEY (id) );"
    return query
def create_tables():
    query = "CREATE TABLE user_invoices ( id int NOT NULL  IDENTITY(1, 1), file_name varchar(255) NOT NULL, user_id int, status int, updated_datetime datetime, PRIMARY KEY (id) );"
    return query

def Alter_auth_user():
    query = "Alter table auth_user add company_name varchar(200);Alter table auth_user add profile_img varchar(255) ; "
    query = query + "Alter table auth_user add last_updated datetime;Alter table auth_user add is_online int; "
    return query

def Alter_auth_user():
    query = "Alter table auth_user add company_name varchar(200);Alter table auth_user add profile_img varchar(255)"
    return query

def Alter_form_fields_mapping():
    query = "Alter table form_fields_mapping add config_uuid varchar(32);Alter table form_fields_mapping add config_name varchar(200);"
    return query

def Alter_user_invoices():
    query = "Alter table user_invoices add invoice_uid varchar(200); alter table user_invoices add config_id varchar(32)"
    return query 
def truncate_data():
    query = "truncate table accuracy_info;truncate table predicted_data;truncate table predicted_table_data;truncate table audited_data;truncate table predicted_table_data;truncate table form_fields_mapping;truncate table form_fields_master;truncate table form_fields_master;truncate table user_invoices"
