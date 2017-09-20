import os
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

print("You must adjust the settings on the source email account to allow for other applications to have access.  Search the internet for instructions for your specific email provider")



srcEmail = "src@email.com"
destEmail = "dst@email.com"

msg = MIMEMultipart()
msg["From"] = sourceEmail
msg['To'] = destEmail
msg["Subject"] = "aaaaaaIntruder Detected!"

messageBody = "this is the body of the email. put whatever you like in here."

msg.attach(MIMEText(messageBody))

def attachImage(fileName):
    try:
        image = open(fileName, "rb").read()
        img = MIMEImage(image, name=os.path.basename(fileName))
        global msg
        msg.attach(img)
    except Exception as e:
	    print("Failed to attach image.")
	    print(e.message)
    finally:
	    return


def sendEmail(fileName, msg):
    try:
        smtp = smtplib.SMTP('smtp.gmail.com:587')
        smtp.starttls()
        smtp.login(srcEmail, 'passwordHere')
    except:
        print("connection failed.")
        traceback.print_exc()
        return

    attachImage(fileName)

    try:
        smtp.sendmail(msg["From"], msg["To"], msg.as_string())
        print("Mail sent!")
    except:
        print("Mail not sent.")
        traceback.print_exc()
    finally:
        smtp.close()
        return

#inside loop
#path = str(date) + ".jpg")
#camera.capture(path)
#sendEmail("2017-06-12_18:06:03.jpg", msg)
