import smtplib
from configparser import ConfigParser
import os
import mimetypes
from sys import argv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

def send_email():
    assert len(argv) == 2, "Incorrect number of arguments"
    config_location = argv[1]
    parser = ConfigParser()
    parser.read(config_location)

    sender_email = parser["sender"]["email"]
    sender_password = parser["sender"]["password"]
    emails_dir = parser["paths"]["emails_dir"]
    template_path = parser["paths"]["template_path"]
    attachments_path = parser["paths"]["attachments_path"]

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        with open(template_path) as file:
            template = file.read()
    except IOError:
        return "error opening an html template"

    try:
        server.login(sender_email, sender_password)
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["Subject"] = "Virus"
        msg.attach(MIMEText(template, "html"))

        for file in os.listdir(attachments_path):
            filename = os.path.basename(file)
            ftype, encoding = mimetypes.guess_type(file)
            file_type, subtype = ftype.split("/")

            if file_type == "text":
                with open(f"{attachments_path}/{file}") as f:
                    file = MIMEText(f.read())
            elif file_type == "image":
                with open(f"{attachments_path}/{file}", "rb") as f:
                    file = MIMEImage(f.read(), subtype)
            elif file_type == "application":
                with open(f"{attachments_path}/{file}", "rb") as f:
                    file = MIMEApplication(f.read(), subtype)
            else:
                return "Unknown type"

            file.add_header('content-disposition', 'attachment', filename=filename)
            msg.attach(file)

        for email_file in os.listdir(emails_dir):
            with open(f"{emails_dir}/{email_file}", "r", encoding="utf-8") as file:
                for receiver_email in file.read().splitlines():
                    msg["To"] = receiver_email
                    server.sendmail(sender_email, receiver_email, msg.as_string())

        return "The message was sent successfully!"
    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"

if __name__ == "__main__":
    print(send_email())
