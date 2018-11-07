import smtplib
from email.mime.text import MIMEText

# me == the sender's email address
# you == the recipient's email address
def sendMail(message, recipient):
    msg = MIMEText(message)
    msg['Subject'] = 'Forgot Password'
    msg['From'] = 'airlinesss@selimkilicaslan.com'
    msg['To'] = recipient

    # Send the message via our own SMTP server.
    s = smtplib.SMTP('77.245.159.15', 587)
    s.login('airlinesss@selimkilicaslan.com','AirlineSSS1')
    s.send_message(msg)
    s.quit()