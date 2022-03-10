import smtplib
from configparser import ConfigParser
import os
from sys import argv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email():
    assert len(argv) == 2, "Incorrect number of arguments"
    config_location = argv[1]
    parser = ConfigParser()
    parser.read(config_location)

    sender_email = parser["sender"]["email"]
    sender_password = parser["sender"]["password"]
    emails_dir = parser["paths"]["emails_dir"]
    template_path = parser["paths"]["template_path"]

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    with open(template_path, "r", encoding="utf-8") as file:
        template = file.read()

    try:
        server.login(sender_email, sender_password)
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["Subject"] = "Важное Обращение"
        msg.attach(MIMEText(template, "html"))

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
