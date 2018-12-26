#!/usr/bin/python

import requests
import json
import time
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
import csv

#Private credentials file, used to make life easy when I deploy new scripts and also to pull variables in across scripts.
import cred


email_server = cred.email_server
me = cred.sm_sender

you = cred.sm_receiver

key = cred.key
base_url = 'https://api.meraki.com/api/v0'
networkid = cred.sm_networkid

headers = {'X-Cisco-Meraki-API-Key': (key), 'Content-Type': 'application/json'}

# all of the available fields in case I want to make it more complex later or need additional info. No matter what though the default fields are always there.
#defaultfields = ['id', 'name', 'tags', 'ssid', 'wifiMac', 'osName', 'systemModel', 'uuid', 'serialNumber']
#possiblefields = ['ip', 'systemType', 'availableDeviceCapacity', 'kioskAppName', 'biosVersion', 'lastConnected', 'missingAppsCount', 'userSuppliedAddress', 'location', 'lastUser', 'publicIp', 'phoneNumber', 'diskInfoJson', 'deviceCapacity', 'isManaged', 'hadMdm', 'isSupervised', 'meid', 'imei', 'iccid', 'simCarrierNetwork', 'cellularDataUsed', 'isHotspotEnabled', 'createdAt', 'batteryEstCharge', 'quarantined', 'avName', 'avRunning', 'asName', 'fwName', 'isRooted', 'loginRequired', 'screenLockEnabled', 'screenLockDelay', 'autoLoginDisabled', 'hasMdm', 'hasDesktopAgent', 'diskEncryptionEnabled', 'hardwareEncryptionCaps', 'passCodeLock']

geturl = '{0}/networks/{1}/sm/devices?fields=lastConnected'.format(str(base_url), str(networkid))

dashboard = requests.get(geturl, headers=headers)

dashboard_json = json.loads(dashboard.text)

with open('ipad_status.csv', mode='w') as csv_file:
    fieldnames = ['Name', 'Last Connected']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for i in dashboard_json['devices']:
        writer.writerow({'Name': i['name'], 'Last Connected': time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(i['lastConnected']))})

# Send email to individuals with just the info requested on the devices.

# me == the sender's email address
# you == the recipient's email address
msg = MIMEMultipart()
msg['Subject'] = 'Current connection status of Ipads'
msg['From'] = me
msg['To'] = you

part = MIMEBase('application', "octet-stream")
part.set_payload(open("ipad_status.csv", "rb").read())
Encoders.encode_base64(part)

part.add_header('Content-Disposition', 'attachment; filename="ipad_status.csv"')

msg.attach(part)

# Send the message via our own SMTP server, but don't include the
# envelope header.
s = smtplib.SMTP(email_server)
s.sendmail(me, you, msg.as_string())
s.quit()
