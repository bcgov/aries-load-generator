from locust import SequentialTaskSet, task, User, between
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
        

    def on_stop(self):
        self.client.shutdown()

    @task
    def get_invite_and_cred(self):
        # Get Invite
        self.invite = {'invitation_url': INVITATION_URL}

        # Accept Invite
        self.client.ensure_is_running()
        connection = self.client.accept_invite(self.invite['invitation_url'])
        self.connection = connection

        # print(f"Connection ID: {self.connection['connectionId']}")
        # print(f"OOB ID: {self.connection['oobRecordId']}")

        # Receive Credential
        credential = self.client.receive_credential(self.connection['did'])

        # Delete Connection
        self.client.delete_connection(self.connection["oobRecordId"])


    # @task
    # def get_invite(self):
    #     # make a blank invite object and set invitation_url to the env var
    #     # for this use case the invitation is created outside of testing and pre-supplied
    #     self.invite = {'invitation_url': INVITATION_URL}

    # @task
    # def accept_invite(self):
    #     self.client.ensure_is_running()
    #     connection = self.client.accept_invite(self.invite['invitation_url'])
    #     self.connection = connection

    # @task
    # def receive_credential(self):
    #     credential = self.client.receive_credential(self.connection)

class Issue(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = between(float(os.getenv('LOCUST_MIN_WAIT',0.1)), float(os.getenv('LOCUST_MAX_WAIT',1)))
#    host = "example.com"