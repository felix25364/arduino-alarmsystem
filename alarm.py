#!/usr/bin/env python3
# Importieren von allen benötigten Biblotheken für das Email senden, interagieren mit Bildern etc.
import smtplib                                           # Importieren der SMTP Biblothek
from email.message import EmailMessage                   # Importieren der Email-Nachricht Biblothek
import os                                                # Importieren der Biblothek zum Bilder lesen und löschen
import shutil                                            # Importieren der Biblothek zum Verschieben der Bilder
import time                                              # Importieren der Biblothek zum Warten
import subprocess                                        # Importieren der Bibliothek zum Starten und Steuern von Prozessen
from threading import Thread                             # Importieren der Bibliothek zum Erstellen und Verwalten von Threads
from pyftpdlib.authorizers import DummyAuthorizer        # Importieren der Dummy-Authorizer-Bibliothek für einfache Benutzerverwaltung
from pyftpdlib.handlers import FTPHandler                # Importieren des FTP-Handlers zur Bearbeitung von FTP-Anfragen
from pyftpdlib.servers import FTPServer                  # Importieren der FTP-Server-Bibliothek zum Starten des FTP-Servers

# Definieren aller wichtigen Daten für die Email (SMTP Server- und Login-Daten und Sender und Empfänger Email)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "haunfelix63@gmail.com"
SMTP_PASS = "cqyd yskc fpbh pmff"
FROM_EMAIL = SMTP_USER
TO_EMAIL = "felix@felix2536.de" # mehrere mit Komma getrennt in Anführungstrichen angeben (z.b. "felix@felix25364.de, haunfelix63@pm.me")

# Definieren der Ordner
FTP_DIR = os.path.abspath("./foto-usent")
DST_DIR = os.path.abspath("./foto-sent")

# Definieren des Speicherortes des Anruf-Scripts und der Telefonnummern
CALL_SCRIPT = "./call.sh"
PHONE_NUMBERS = ["015906317338", "015229256078"]  # bis zu 5 Nummern mit "," getrennt und in ""

# Definieren der Warte und Überprüfungs Intervalle
WAIT_TIME = 20
CHECK_INTERVAL = 5

# Funktion für das Abrufen das Anrufscripts
def trigger_calls():
    try:
        args = [CALL_SCRIPT] + PHONE_NUMBERS[:3]
        subprocess.run(args, check=True)
        print(f"Call-Skript aufgerufen mit Nummer(n): {', '.join(PHONE_NUMBERS[:3])}")
    except Exception as e:
        print(f"Fehler beim Aufrufen des Call-Skripts: {e}")


# Funktion für das Senden der Emails mit Bildern als Anhang
def send_email_with_attachments(file_paths):
    msg = EmailMessage()
    msg['Subject'] = "Unbefugter Zutritt"   # Setzten des Betreffs der Email
    msg['From'] = FROM_EMAIL                # Setzten der Sender Email-Adresse anhand der oben definierten Variable
    msg['To'] = TO_EMAIL                    # Setzten der EMpfänger Email-Adresse anhand der oben definierten Variable
    msg.set_content("Unbefugter Zutritt erkannt – siehe Anhang")
    for file_path in file_paths:
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(file_path)
                msg.add_attachment(file_data, maintype='image', subtype='jpeg', filename=file_name)
        except Exception as e:
            print(f"Fehler beim Lesen von {file_path}: {e}")
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
        print(f"E-Mail mit {len(file_paths)} Bildern gesendet.")
        return True
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")
        return False


# Funktion für das verschieben der Bilder, sodass diese nicht mehrfach versandt werden.
def move_files(file_paths, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for file_path in file_paths:
        try:
            shutil.move(file_path, dst_dir)
            print(f"{os.path.basename(file_path)} verschoben nach {dst_dir}")
        except Exception as e:
            print(f"Fehler beim Verschieben von {file_path}: {e}")


# Schleife zum erkennen von neuen Bildern
def monitoring_loop():
    print("Überwachung gestartet – warte auf neue Bilder...")
    while True:
        file_paths = [os.path.join(FTP_DIR, f) for f in os.listdir(FTP_DIR)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]    # Nur Bilddateien erkennen, um Fehlalarme zu verhindern
        if file_paths:
            print(f"{len(file_paths)} neue Datei(en) gefunden. Warte {WAIT_TIME} Sekunden...")  # Warten um alle Bilder zu senden
            time.sleep(WAIT_TIME)
            file_paths = [os.path.join(FTP_DIR, f) for f in os.listdir(FTP_DIR)
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if file_paths and send_email_with_attachments(file_paths):
                trigger_calls()
                move_files(file_paths, DST_DIR)
        time.sleep(CHECK_INTERVAL)


# Funktion zum Hosten des FTP Servers
def start_ftp_server():
    authorizer = DummyAuthorizer()
    authorizer.add_user("felix", "geheim", FTP_DIR, perm="elradfmw") # Setzten des Nutzernamens, Passworts, des Ordners (oben in der Variable FTP_DIR definiert) und setzten der Berechtigungen für diesen Nutzer

    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer(("0.0.0.0", 21), handler) # FTP-Server auf Port 21 starten und setzten, dass er auf jede IP und jedes Interface hört
    print("FTP-Server läuft auf Port 21")
    server.serve_forever()

if __name__ == "__main__":
    # Verzeichnisse anlegen falls nicht vorhanden
    for d in [FTP_DIR, DST_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
    # Monitoring und FTP parallel starten
    monitor_thread = Thread(target=monitoring_loop)
    monitor_thread.daemon = True
    monitor_thread.start()
    start_ftp_server()

