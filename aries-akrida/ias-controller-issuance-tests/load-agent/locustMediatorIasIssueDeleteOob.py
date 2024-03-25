from locust import SequentialTaskSet, task, User, between
from locust.exception import StopUser

from locustClient import CustomClient
import time
import inspect
import json

import fcntl
import os
import signal

WITH_MEDIATION = os.getenv("WITH_MEDIATION")
INVITATION_URL = os.getenv("INVITATION_URL")

class CustomLocust(User):
    abstract = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

        # override the issuer with our custom IAS one
        from issuerAgent.iasController import IasControllerIssuer
        
        self.client = CustomClient(self.host)
        self.client.issuer = IasControllerIssuer()

class UserBehaviour(SequentialTaskSet):
    def on_start(self):
        self.client.startup(withMediation=bool(WITH_MEDIATION))
        self.counter = 0 # add a counter attribute

    def on_stop(self):
        self.client.shutdown()

    @task
    def recieve_invitation(self):
        # Get Invite url from env
        self.invite = {'invitation_url': INVITATION_URL}

        # Accept Invite
        self.client.ensure_is_running()
        connection = self.client.accept_invite(self.invite['invitation_url'], True)
        
        # print(f"Connection ID: {self.connection['connectionId']}")
        # print(f"OOB ID: {self.connection['oobRecordId']}")

        self.connection = connection

    @task
    def call_ias_for_cred_and_recieve(self):
        self.client.ensure_is_running()

        # Call the IAS "/next" endpoint to issue the credential  
        # Agent handles recieving the credential states internally
        iasResponseBody = self.client.receive_credential(self.connection['did'])

    @task
    def delete_oob_record(self):
        self.client.ensure_is_running()
        
        # Remove the OOB record so next loop it can get invite again
        self.client.delete_oob(self.connection["oobRecordId"])

        # uncomment and adjust counter val if you want a limit per user 
        # self.counter += 1
        # if self.counter == 10:
        #     print("Limit reached for user")
        #     raise StopUser()


class Issue(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = between(float(os.getenv('LOCUST_MIN_WAIT',0.1)), float(os.getenv('LOCUST_MAX_WAIT',1)))
#    host = "example.com"