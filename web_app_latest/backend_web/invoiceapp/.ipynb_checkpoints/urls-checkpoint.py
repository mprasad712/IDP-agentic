from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views, api_views, api_invoice_process, api_invoice_upload, api_user, views_user, views_contract, views_agentic
from django.views.static import serve
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Different APIs for React - created by IDP
    re_path(r'^manifest\.json$', serve, {
        'document_root': '/data/SDLC/web_app/frontend_web/build',
        'path': 'manifest.json',
    }),
    path('admin/', admin.site.urls),
    path('dashboard_data/', views.get_dashboard_data, name='get_dashboard_data'),
    path('dashboard_data_weekly/', views.get_dashboard_data_weekly, name='get_dashboard_data_weekly'),
    path('config_data/', views.config_list, name='config_list'),
    path('processed/', views.processed, name='processed_data'),
    path('validated/', views.validated, name='validated'),
    path('invoicedeleted/', views.invoicedeleted, name='invoicedeleted'),
    path('stpsupplier/', views.stpsupplier, name='stpsupplier'),
    path('processlog/', views.processlog, name='processlog'),
    path('agentic_hub/', views_agentic.agentic_hub, name='agentichub'),
    path('get_agent_data/', views_agentic.get_agent_data, name='get_agent_data'),
    path('get_configuration_agent_data/', views_agentic.get_configuration_agent_data, name='get_configuration_agent_data'),
    path('get_all_agent_data/', views_agentic.get_all_agent_data, name='get_all_agent_data'),
    path('get_project_names/', views_agentic.get_project_names, name='get_project_names'),
    path('run_agentic_project/', views_agentic.run_agentic_project, name='run_agentic_project'),
    path('delete_project/', views_agentic.delete_project, name='delete_project'),
    path('update_agentic_project/', views_agentic.update_agentic_project, name='update_agentic_project'),
    path('get_agentic_project_running_status/', views_agentic.get_agentic_project_running_status, name='get_agentic_project_running_status'),
    path('update_agentic_project_running_status/', views_agentic.update_agentic_project_running_status, name='update_agentic_project_running_status'),
    path('extracted_fields_idp/', api_views.extracted_fields_idp, name='extracted_fields_idp'),
    path('view_configuration/', views.view_configuration, name='view_configuration'),
    path('delete_field_config/', api_views.delete_field_config, name='delete_field_config'),
    path('get_audited_data/', api_views.get_audited_data, name='get_audited_data'),
    path('get_predict_data/', api_views.get_predict_data, name='get_predict_data'),
    path('auditSubmit/', api_views.auditSubmit, name="auditSubmit"),
    path('session_data/', views.session_data, name='session_data'),
    path('get_agent_process_live_status/', views_agentic.get_agent_process_live_status, name='get_agent_process_live_status'),
    
    path('userlist/', views.userlist, name='userlist'),
    path('', views.index, name='index'),  # Correct empty path
    path('terms_and_condition/', views.terms_and_condition, name='terms_and_condition'),
    path('change_password/', views.change_password, name='changepassword'),

    # Use re_path when regex is appropriate
    re_path(r'^audit_detail/(?P<pk>[0-9a-zA-Z]+)/$', views.audit_detail, name="audit_detail"),
    re_path(r'^audit/(?P<pk>[0-9a-zA-Z]+)/$', views.audit, name="audit"),
    
    path('runidp/', views.runidp, name='runidp'),
    path('define_layout/', views.define_layout, name='define_layout'),
    path('upload_invoice/', views.upload_invoice, name='upload_invoice'),
    path('download/', views.download, name='download'), 
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('authlogout/', auth_views.LogoutView.as_view(), name='logout'),

    # Correcting logout path definition
    path('logout/', views.logout, name='logout'),
    
    # Confirm no repetitive paths
    path('add_fields_configuration/', api_views.add_fields_configuration, name='add_fields_configuration'),
    path(r'download_multiple_audit/',views.download_multiple_audit, name="download_multiple_audit"),
    # path('add_fields_configuration_dynamic/', api_views.add_fields_configuration_dynamic, name='add_fields_configuration_dynamic'),
    path('delete_field_config/', api_views.delete_field_config, name='delete_field_config'),
    path('deletedprocessedRecords/', api_views.deletedprocessedRecords, name="deletedprocessedRecords"),
    re_path(r'^download_audit_excel/$', views.download_audit_excel, name="download_audit_excel"),
    re_path(r'^getbusinessrule_fields/$', views.getbusinessrule_fields, name="getbusinessrule_fields"),
    
    # User
    path('user/profile/', views_user.profile, name='user_profile'),
    path('user/upload_profile_pic/', api_user.upload_profile_pic, name='user/upload_profile_pic'),
    path('user/upload_organization_pic/', api_user.upload_organization_pic, name='user/upload_organization_pic'),
    path('user/update_profile/', api_user.update_profile, name='user/update_profile'),
    
    # Upload invoice paths
    path('upload_ricefile/', api_invoice_upload.upload_ricefile, name='upload_ricefile'),
    path('upload_voicefile/', api_invoice_upload.upload_voicefile, name='upload_voicefile'),
    path('uploadfile/', api_invoice_upload.uploadfile, name='uploadfile'),
    path('uploadmultiplefiles/', api_invoice_upload.uploadmultiplefiles, name='uploadmultiplefiles'),
    path('is_upload_allow/', api_invoice_upload.is_upload_allow, name='is_upload_allow'),
    path('delete_invoice_file/', api_invoice_upload.delete_invoice_file, name='delete_invoice_file'),
    
    path('invoiceprocess/', api_invoice_process.invoiceprocess, name='invoiceprocess'),
    
    path('addsupplier/', api_views.addsupplier, name='addsupplier'),

    # Suppliers
    path('stprules/', views.stprules, name='stprules'),

    # Login & Registration
    path('loginprocess/', api_views.loginprocess, name='loginprocess'),
    path('registeruser/', api_views.registeruser, name='registeruser'),
    path('getuserInfo/', views.getuserInfo, name='getuserInfo'),
    re_path(r'^updateuser/$', views.updateuser, name="updateuser"),
    re_path(r'^takeatour/$', views.takeatour, name="takeatour"),

    # User Authentication
    re_path(r'user_authentication/(?P<pk>[0-9a-zA-Z]+)/$', views.user_authentication, name='user_authentication'),
    path('api_activate_user/', views.api_activate_user, name='api_activate_user'),
    
    # Feedback
    path('feedbacksubmit/', views.feedbacksubmit, name='feedbacksubmit'),
    path('feedback/', views.feedback, name='feedback'),
    
    # Contract Management
    path('contract_configuration/', views_contract.contract_configuration, name='contract_configuration'),
    path('contract_dashboard/', views_contract.contract_dashboard, name='contract_dashboard'),
    path('rclassification/', views.rclassification, name='rclassification'),
    path('vauth/', views.vauth, name='vauth'),
    path('vauthaccount/', views.vauthaccount, name='vauthaccount'),

    # Catch-all pattern for client-side routing in the React app
    re_path(r'^(?:.*)/?$', TemplateView.as_view(template_name='index.html')),
]