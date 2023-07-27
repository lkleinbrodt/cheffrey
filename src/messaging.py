import streamlit as st
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

carriers = {
    'att': 'txt.att.net',
    'verizon': 'vtext.com',
    'tmobile': 'tmomail.net',
    'sprint': 'messaging.sprintpcs.com',
}



def text_meal_plan(phone_number, meal_plan):
    email_address = 'lkleinbrodt@gmail.com'
    try:
        email_password = st.secrets['email_password']
        
    except FileNotFoundError:
        email_password = os.getenv('email_password')
    
    phone_carrier_domain = carriers['att'] #TODO: try all combos
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = f"{phone_number}@{phone_carrier_domain}"

    html_part = MIMEText(meal_plan, 'html')
    msg.attach(html_part)
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(email_address, email_password)

        # Send the message
        server.sendmail(
            email_address, 
            f"{phone_number}@{phone_carrier_domain}", 
            msg.as_string()
        )

import re
def send_meal_plan(meal_plan):
    num = st.session_state['phone_number']
    if bool(re.search(r'[^0-9-]', num)):
        st.warning('Phone numbers should only contain numbers and hyphens')
        return False
    # Replace all non-numeric characters with an empty string
    num = re.sub(r'[^0-9]+', '', num)
    if len(num) != 10:
        st.warning('Phone number must have 10 digits')
        return False
    
    try:
        text_meal_plan(phone_number=num, meal_plan = meal_plan)
    except Exception as e:
        logger.error(e)
        st.warning('Sorry. failed to text you') 