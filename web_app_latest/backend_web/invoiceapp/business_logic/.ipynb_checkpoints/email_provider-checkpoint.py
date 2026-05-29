import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class email_provider:

    def __init__(self):
        pass     

     
    def create_subject(self):
        return "New User Sign up!!"

    def email_body(self,user_uuid, user_name,first_name, last_name,email,email_settings,auth_pin,auth_code):
        
        '''html = """\
        <html>
        <head></head>
        <body>
            <table>
            <tr style='line-height:32px;'>
            <td colspan="2">Hi Team!</td>
            </tr>
            <tr style='line-height:32px;'>
            <td colspan="2">New user request is raised by  <b>""" +first_name +""" </b>.</td>
            </tr><tr style='line-height:32px;'><td>Name</td><td>""" +first_name +""" """ +last_name +"""</td></tr>
            <tr style='line-height:32px;'><td>Email</td><td>""" +email+""" </td></tr> 
            <tr style='line-height:32px;'><td colspan="2" >Please use below link to activate user.</td></tr>
            <tr style='line-height:32px;'><td colspan = "2">Link URL : <a href="""+ auth_code+""/""+ auth_code+ """">http://10.13.32.85:5000/idp/""" +auth_code +"""</a> </td>
            <tr style='line-height:32px;'><td colspan = "2"> Activation Code : """+ auth_pin +""" <br>
            <strong>Regards</strong> <br>
            Idp Team
            </td>
            </tr>
            </table>
 
        </body>
        </html>
        """'''
        html = "<html><body><head></head><title></title><h2>Thanks for sending mail</h2></body></html>"
        return html

    def sent_mail(self,user_uuid, user_name,first_name, last_name,email,email_settings,auth_pin,auth_code):
        print("send email function call")
        sender_email = "email_id"
        recipient_email = email

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] =  self.create_subject()
        msg['From'] = sender_email
        msg['To'] = recipient_email 
        
        html_body = self.email_body(user_uuid, user_name,first_name, last_name,email,email_settings,auth_pin,auth_code) 
        print(html_body)
        part2 = MIMEText(html_body, 'html') 
        msg.attach(part2)

        # Send the message via local SMTP server.
        s = smtplib.SMTP('localhost')
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(sender_email, recipient_email, msg.as_string())
        s.quit()
        print("send email successfully")



