from datetime import datetime
from bs4 import BeautifulSoup
import requests, os
import pandas as pd
import os,json

GENERAL_WEBHOOK_SECRET_DEV="**************"
HOOK_URL = "https://hooks.slack.com/services/%s" % GENERAL_WEBHOOK_SECRET_DEV
current_dateTime = str(datetime.now()).split(" ")[0].split("-")[2]

class BankingCircle:
    
    def __init__(self, link):
        self.link = link
        self.soup = BeautifulSoup(requests.get(self.link).text, 'html.parser')
        self.incident_detected = []
        
    def get_link(self):
        return self.link
    
    def detect_incident(self):
        results_incidents_containers_list = self.soup.find_all("div", class_="incidents-list format-expanded")
        for element in results_incidents_containers_list:
            validating_for_incident_recodrs =str(element.find_all("strong")[0]).split("<")[1].split(">")[0]
            if "strong" in validating_for_incident_recodrs:
                incident_statuses = element.find_all("strong")[0].string
                incident_date_parse=str(element.find_all("small")[0]).split(" ")
                incident_date=incident_date_parse[14].split(">")[1].split("<")[0]

                if incident_date == current_dateTime:
                    self.incident_detected.append([incident_statuses,
                                                    incident_date_parse[12],
                                                    incident_date_parse[14].split(">")[1].split("<")[0], 
                                                    incident_date_parse[16].split(">")[1].split("<")[0],
                                                    str(datetime.now()).split(" ")[0].split("-")[0]])

                    return pd.DataFrame(self.incident_detected[0]).T.rename(columns={0:"Status",
                                                                                     1:"Month",
                                                                                     2:"Date",
                                                                                     3:"Time",
                                                                                     4:"Year"})
                elif incident_date != current_dateTime:
                    no_incidents_dates=element.find_all("div", class_="status-day font-regular no-incidents")
                
                    for line in no_incidents_dates:
                        dates=line.find_all("div", class_="date border-color font-large")
                        incident_status=line.find_all("p", class_="color-secondary")
                        self.incident_detected.append([str(dates)[43:46],str(dates)[68:70],str(dates)[99:103], str(incident_status)[28:49]])
                    
                    return pd.DataFrame(self.incident_detected, columns=["Month",
                                                                         "Date",
                                                                         "Year",
                                                                         "Status"])

            

results=BankingCircle('https://bankingcircleconnect.statuspage.io/#past-incidents').detect_incident()       
nl = '\n'
text = f"<!subteam*******> BankingCircle Incident Notification {nl}{results}"
slack_message = {'text': text, 'Attachment': "Notification! "}
#print(slack_message)
req = requests.post(HOOK_URL, json.dumps(slack_message))