#!/usr/bin/env python3

import smtplib
from email.message import EmailMessage
import shutil
import time
import subprocess
import os
from threading import Thread
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USER = "mail@example.com"
SMTP_PASS = "your_password"

FROM_EMAIL = SMTP_USER
TO_EMAIL = "target@example.com"

FTP_DIR = os.path.abspath("./foto-usent")
DST_DIR = os.path.abspath("./foto-sent")
FTP_USER = "user"

CALL_SCRIPT = "./call.sh"
PHONE_NUMBERS = ["0123456789", "911"]

WAIT_TIME = 20
CHECK_INTERVAL = 5

def trigger_calls():
    try:
        args = [CALL_SCRIPT] + PHONE_NUMBERS[:3]
        subprocess.run(args, check=True)
        print(f"Triggered: {', '.join(PHONE_NUMBERS[:3])}")
    except Exception as e:
        print(f"Error: {e}")

def send_email_with_attachments(file_paths):
    msg = EmailMessage()
    msg['Subject'] = "Alert"
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg.set_content("Detection alert - see attachments.")

    for file_path in file_paths:
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(file_path)
                msg.add_attachment(file_data, maintype='image', subtype='jpeg', filename=file_name)
        except Exception as e:
            print(f"Read error {file_path}: {e}")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
        print(f"Sent {len(file_paths)} images.")
        return True
    except Exception as e:
        print(f"SMTP error: {e}")
        return False

def move_files(file_paths, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for file_path in file_paths:
        try:
            shutil.move(file_path, dst_dir)
            print(f"Moved {os.path.basename(file_path)}")
        except Exception as e:
            print(f"Move error {file_path}: {e}")

def monitoring_loop():
    while True:
        file_paths = [os.path.join(FTP_DIR, f) for f in os.listdir(FTP_DIR)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if file_paths:
            trigger_calls()
            time.sleep(WAIT_TIME)
            file_paths = [os.path.join(FTP_DIR, f) for f in os.listdir(FTP_DIR)
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if file_paths and send_email_with_attachments(file_paths):
                move_files(file_paths, DST_DIR)
        time.sleep(CHECK_INTERVAL)

class CustomAuthorizer(DummyAuthorizer):
    def validate_authentication(self, username, password, handler):
        if not self.has_user(username):
            return False
        return True

def start_ftp_server():
    authorizer = CustomAuthorizer()
    authorizer.add_user(FTP_USER, "secret - doesnt acutally matter", FTP_DIR, perm="elradfmw")
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer(("0.0.0.0", 21), handler)
    server.serve_forever()

if __name__ == "__main__":
    for d in [FTP_DIR, DST_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
    monitor_thread = Thread(target=monitoring_loop)
    monitor_thread.daemon = True
    monitor_thread.start()
    start_ftp_server()
