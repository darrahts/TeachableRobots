import os
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#   You must adjust the settings on the source email account to allow for
#   other applications to have access.  Search the internet for instructions
#   for your specific email provider


class EmailSender(object):

    def __init__(self, srcEmail):
        self.srcEmail = srcEmail
        self.srcPass = "password123"
        self.msg = MIMEMultipart()
        return


    def SetMessageData(msgFrom=self.srcEmail, destEmail, msgSubject, msgBody):
        self.msg["From"] = msgFrom
        self.msg['To'] = destEmail
        self.msg["Subject"] = msgSubject
        self.msg.attach(MIMEText(msgBody))
        return

    def AttachImage(fileName):
        try:
            image = open(fileName, "rb").read()
            img = MIMEImage(image, name=os.path.basename(fileName))
            global msg
            self.msg.attach(img)
            return True
        except Exception as e:
            print("Failed to attach image.")
            print(e.message)
            return False


    def SendEmail():
        try:
            smtp = smtplib.SMTP('smtp.gmail.com:587')
            smtp.starttls()
            smtp.login(srcEmail, self.srcPass)
        except:
            print("connection failed.")
            traceback.print_exc()
            return

        try:
            smtp.sendmail(self.msg["From"], self.msg["To"], self.msg.as_string())
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
