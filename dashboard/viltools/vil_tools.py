import logging
import requests
import gzip
import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

# #######################################################################
# Parsing d'un fichier de conf qui retourne un dictionnaire clé/Valeur
# #######################################################################
def config_dict(filename):
    """Convert content of config-file into dictionary."""
    with open(filename, "r") as f:
        cfglines = f.readlines()
    cfgdict = {}
    for line in cfglines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        key_value = line.split("=")
        if len(key_value)==1 :
            print("Bad line in config-file %s:\n%s" % (filename,line))
            continue
        key,value=key_value[0],"=".join(key_value[1:])
        key = key.strip()
        value = value.strip()
        if value in ["True", "False", "None", "''", '""']:
            value = eval(value)
        else:
            try:
                if "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass # value need not be converted
        cfgdict[key] = value
    return cfgdict

# #############################################################
# Initialisation Fwk Python (logging + Fichier de conf
# In : emplacement/nom du fichier de conf
# Out : Dictionnaire cle/valeur correspondant au fichier de conf
# #############################################################
def fwk_init(conf_file) :
    myconf = config_dict(conf_file)
    logging.basicConfig(filename=myconf["LOG_FILE"],level=myconf["LOG_LEVEL"],format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S %p')
    return myconf
# #################################################################
# Decompresse une URM contenant un fichier zip vers fichier cible
###################################################################
def uncompressURL(url,filename,proxy) :
    res = requests.get(url,proxies=proxy)
    file_content=gzip.decompress(res.content)
    with open(filename,'wb') as f2 :
        f2.write(file_content)

# ####################################################
# Envoi de mail
# ####################################################

def send_mail( send_from, send_to, subject, text, files=[], server="localhost", port=587, username='', password='', isTls=True):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = subject
    msg.attach( MIMEText(text) )
    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
        msg.attach(part)
        smtp = smtplib.SMTP(server, port)
        if isTls:
            smtp.starttls()
        smtp.login(username,password)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.quit()
