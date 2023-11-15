from datetime import datetime
from bs4 import BeautifulSoup
import requests, os
import pandas as pd
import os,json

GENERAL_WEBHOOK_SECRET_DEV="*****************************************************"
HOOK_URL = "https://hooks.slack.com/services/%s" % GENERAL_WEBHOOK_SECRET_DEV
current_dateTime = str(datetime.now()).split(" ")[0].split("-")[2]
nl = '\n'

class BankingCircle:
    
    def __init__(self, link):
        self.link = link
        self.soup = BeautifulSoup(requests.get(self.link).text, 'html.parser')
        self.incident_detected = []
    # save link for scraping, not nessesary to have it  
    def get_link(self):
        return self.link
    #parce web page to detect if there was an incident at the moment
    def detect_incident(self):
        results_incidents_containers_list = self.soup.find_all("div", class_="incidents-list format-expanded")
        for element in results_incidents_containers_list:
            validating_for_incident_recodrs =str(element.find_all("strong")[0]).split("<")[1].split(">")[0]
            if "strong" in validating_for_incident_recodrs:
                incident_statuses = element.find_all("strong")[0].string
                incident_date_parse=str(element.find_all("small")[0]).split(" ")
                incident_date=incident_date_parse[14].split(">")[1].split("<")[0]
                #incedent detected and preparing the notification, incident message notification will be modified to the user friendly message
                if incident_date == current_dateTime:
                    self.incident_detected.append([incident_statuses,
                                                    incident_date_parse[12],
                                                    incident_date_parse[14].split(">")[1].split("<")[0], 
                                                    incident_date_parse[16].split(">")[1].split("<")[0],
                                                    str(datetime.now()).split(" ")[0].split("-")[0]])
                    return self.incident_detected[0]
#prepare a valid format for Slack
def prepare_notification_for_slack(data):
    slack_message = {'text': data, 'Attachment': "Notification! "}
    req = requests.post(HOOK_URL, json.dumps(slack_message))
#sending message to slack
def sending_incident_notificarion(data):
    if data != None:
        results = pd.DataFrame(data).T.rename(columns={0:"Status", 1:"Month", 2:"Date", 3:"Time", 4:"Year"})
        prepare_notification_for_slack(f"<!subteam******> BankingCircle Incident Notification {nl}{results}")
    else:
        prepare_notification_for_slack(f"<!subteam******> BankingCircle Incident Notification {nl} No Incidens Found")
#executing the script
sending_incident_notificarion(BankingCircle('https://bankingcircleconnect.statuspage.io/#past-incidents').detect_incident())
