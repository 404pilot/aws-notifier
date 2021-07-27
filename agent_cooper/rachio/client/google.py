import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import html2text
import httplib2
from googleapiclient import errors, discovery
from oauth2client import client


class Gmail:
    def __init__(self, client_id, client_secret, refresh_token):
        self._credentials = client.GoogleCredentials(
            None,
            client_id,
            client_secret,
            refresh_token,
            None,
            "https://accounts.google.com/o/oauth2/token",
            'my-user-agent'
        )

    def send_message(self, sender, to, subject, msg):
        http = self._credentials.authorize(httplib2.Http())

        service = discovery.build('gmail', 'v1', http=http, cache_discovery=False)

        combined_html_message = """\
        <html>
              <body>
                {msg}
              </body>
        </html>
        """.format(msg=msg)

        msg_html = combined_html_message
        msg_plain = Gmail.html_to_plain_text(combined_html_message)

        message = Gmail.create_message_html(sender, to, subject, msg_html, msg_plain)

        Gmail.send_message_internal(service, "me", message)

    @staticmethod
    def create_message_html(sender, to, subject, msg_html, msg_plain):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to
        msg.attach(MIMEText(msg_plain, 'plain'))
        msg.attach(MIMEText(msg_html, 'html'))
        return {'raw': base64.urlsafe_b64encode(msg.as_string().encode('UTF-8')).decode(
            'ascii')}

    @staticmethod
    def send_message_internal(service, user_id, message):
        try:
            message = (
                service.users().messages().send(userId=user_id, body=message).execute())
            print('Message Id: %s' % message['id'])
        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    @staticmethod
    def html_to_plain_text(html):
        plain = html2text.html2text(html)
        return plain
