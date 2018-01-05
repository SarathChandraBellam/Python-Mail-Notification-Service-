"""
Micro service to send mail with rendered data of Template
"""
__author__ = "Sarath chandra Bellam"

import os
import json
from flask import Flask
from flask_cors import cross_origin
from flask import request
from flask import jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment


app = Flask(__name__)
# Configuring the port
port = int(os.getenv("PORT", 3001))


TEMPLATE =   """
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body>
<pre>Hi Team,</pre>
<br>

<pre>Application Name:{{appName}}</pre>
<pre>Status:{{status}}</pre>
<pre>Time Stamp:{{timestamp}}</pre>
<br>
<pre>Thanks,</pre>
<pre>xxxxxxx</pre>

<hr> </hr>
This is an auto generated mail.Do not reply
</body>
</html>
"""


class MailNotification:
    """

    """
    def __init__(self, smtp_server, from_user, to_user, subject,
                 content, smtp_user, smtp_passkey):
        """

        """
        self.smtp_server = smtp_server
        self.from_user = from_user
        self.recipients = to_user
        self.content = content
        self.login_user = smtp_user
        self.login_key = smtp_passkey
        self.subject = subject
        self.msg = None
        self.smtp = None
        self.status = True
        self.error = None

    def smtp_connect(self):
        """

        """
        try:
            print(self.smtp_server)
            self.smtp = smtplib.SMTP(self.smtp_server, port=25)
        except smtplib.SMTPException  as error_connect:
            self.status = False
            self.error = error_connect
        if self.login_user:
            try:
                self.smtp.login(self.login_user, self.login_key)
            except smtplib.SMTPException as error_login:
                self.status = False
                self.error = error_login

    def render_template(self):
        """

        """
        template_environ = Environment()
        mail_content = template_environ.from_string(TEMPLATE)
        content = mail_content.render(self.content)
        self.msg = MIMEMultipart('alternative')
        self.msg.attach(MIMEText(content, 'html'))

    def send_mail(self):
        """

        """
        self.smtp_connect()
        self.render_template()
        self.msg['Subject'] = self.subject
        self.msg['Reply-to'] = self.from_user
        print(self.msg)
        try:
            self.smtp.sendmail(self.from_user, self.recipients, self.msg.as_string())
        except smtplib.SMTPException as error_send:
            self.status = False
            self.error = error_send


@app.route('/send_mail', methods = ['POST'])
@cross_origin()
def notify_mail_service():
    """
    """
    if request.headers['Content-Type'] == 'application/json':
        user_input = json.loads(request.data.decode(encoding='UTF-8'))
        smtp_server = user_input['server']
        smtp_from_user = user_input['from']
        if isinstance(user_input['to'], list):
            smtp_to_user = user_input['to']
        else:
            smtp_to_user = [user_input['to']]
        subject = user_input['subject']
        content = user_input['data']
        try:
            login_user =  user_input['user']
            login_passkey = user_input['passkey']
        except KeyError:
            login_user = None
            login_passkey = None
        mail_notify = MailNotification(smtp_server, smtp_from_user, smtp_to_user,
                                       subject, content, login_user, login_passkey)
        mail_notify.send_mail()
        if mail_notify.status is True:
            return jsonify({'status': 'SUCCESS'})
        else:
            return jsonify({'status': 'FAILURE', 'remark':mail_notify.error})
    else:
        return jsonify({'status': 'SUCCESS', 'remark':'Content type != application/json'})

if __name__ == '__main__':
    app.run(port=port)





