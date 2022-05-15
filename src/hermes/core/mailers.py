from smtplib import SMTP
from ssl import create_default_context
from email.message import EmailMessage
from typing import Tuple

from hermes.core import notifiers

from hermes.core.exceptions import SkipReciever

class BaseMailer(notifiers.BaseNotifier):
    """
    Base Mailer class, which all mailers should inherit from
    """
  
    DEFAULT_HEADERS = {
        'Subject': 'This is a base title',
    }

    def __init__(self, smtp_port: int=None, smtp_server: str=None, bot_email: str=None, bot_password: str=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if isinstance(smtp_port, int):
            self.smtp_port = smtp_port
        else:
            raise NotImplementedError(f"Add `smtp_port` int attribute, to mailer class, not {type(smtp_port)}")

        if isinstance(smtp_server, str):
            self.smtp_server = smtp_server
        else:
            raise NotImplementedError(f"Add `smtp_server` str attribute, to mailer class, not {type(smtp_server)}")

        if isinstance(bot_email, str):
            self.bot_email = bot_email
        else:
            raise NotImplementedError(f"Add `bot_email` str attribute, to mailer class, not {type(bot_email)}")

        if isinstance(bot_password, str):
            self.bot_password = bot_password
        else:
            raise NotImplementedError(f"Add `bot_password` attribute, to mailer class, not {type(bot_password)}")
      

        self.headers = self.DEFAULT_HEADERS
        self.headers['From'] = self.bot_email

    def send_notifications(self, articles: list, recievers: list) -> None:
        """
        Handles sending emails
        """


        articles = self.prepare_articles(articles)

        tls = create_default_context()
        with SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls(context=tls)
            server.login(self.bot_email, self.bot_password)

            articles, recievers = self.pre_send(articles, recievers, server)

            ex = None
            counter = 0
            try:
                for email in self.generate_sendable_emails(articles, recievers):                
                    server.sendmail(self.bot_email, email['To'], email.as_string())
                    counter += 1
            except Exception as e:
                ex = e

            raise_exception = self.post_send(ex, counter, articles, recievers, server)

            if raise_exception and ex:
                raise ex

    def pre_send(self, articles: list, recievers: list, server: SMTP) -> Tuple[list, list]:
        """
        Executes before sending emails
        """
        return articles, recievers

    def post_send(self, ex: Exception, num_emails_sent: int, articles: list, recievers: list, server: SMTP) -> bool:
        """
        Executes after sending emails 
        """
        return True

    def prepare_articles(self, articles: list) -> list:
        """
        Returns processed articles
        """
        
        return articles


    def generate_sendable_emails(self, articles: list, recievers: list) -> EmailMessage:
        """
        Generator function, constructs EmailMessage with all content
        yields EmailMessage that is ready to send
        """

        msg = EmailMessage()
        
        base_content = self.get_message_base_content()

        headers = self.get_mailer_headers()
        msg = self.add_or_replace_message_headers(msg, headers)


        for reciever in recievers:
            msg.clear_content()
            msg = self.add_or_replace_message_headers(msg, {'To': reciever['address']})
            
            try:
                body = self.get_message_body(articles, reciever)
                content = base_content.format(body)
                msg.add_alternative(content, subtype='html')

                msg = self.edit_message(msg, articles, reciever)
            except SkipReciever as e:
                continue 

            yield msg

    def add_or_replace_message_headers(self, msg: EmailMessage, headers: dict) -> EmailMessage:
        for header in headers.items():
            if header[0] in msg.keys():
                msg.replace_header(*header)
            else:
                msg.add_header(*header)
        return msg

    def edit_message(self, msg: EmailMessage, articles: list, reciever: dict) -> EmailMessage:
        """
        Optional function, hooks into message creation,
        allows programmer to make adjustments to the message just before sending
        must return EmailMessage object
        """
        return msg

    def get_mailer_headers(self) -> dict:
        return self.headers

    def update_mailer_headers(self, new_headers: dict) -> None:
        self.headers.update(new_headers)

    def get_message_body(self, articles: list, reciever: dict) -> str:
        """
        This function should return message body as string
        """
        raise NotImplementedError()

    def get_message_base_content(self) -> str:
        """
        Create and return html skeleton for emails
        """

        # It doesn't work without the str()
        base = str("""\
        <!DOCTYPE html>
        <html>
        <head></head>
        <body>
            {}
        </body>
        </html>
        """
        )
        
        return base
