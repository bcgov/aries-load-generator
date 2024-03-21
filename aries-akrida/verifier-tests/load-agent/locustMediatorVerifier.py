from locust import SequentialTaskSet, task, User, between
from locustClient import CustomClient
import time
import inspect
import json

import fcntl
import os
import signal

WITH_MEDIATION = os.getenv("WITH_MEDIATION")

class CustomLocust(User):
    abstract = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.client = CustomClient(self.host)

class UserBehaviour(SequentialTaskSet):
    def on_start(self):
        self.client.startup(withMediation=bool(WITH_MEDIATION))

        # Invoke the Issuer agent (Traction) to get an invitation and accept it
        invite = self.client.issuer_getinvite()
        connection = self.client.accept_invite(invite['invitation_url'])
        # print(f"DEBUG: Issuer Connection: {connection}")

        # Receive the configured credential
        credential = self.client.receive_credential(invite['connection_id'])
        print(f"DEBUG: Cred result: {credential}")


        # Invoke the Verifier agent (Traction) to get an invitation
        verifier_invite = self.client.verifier_getinvite()
        verifier_connection = self.client.accept_invite(verifier_invite['invitation_url'])
        self.verifier_invite = verifier_invite
        print(f"DEBUG: Verifier Connection: {verifier_connection}")


    def on_stop(self):
        self.client.shutdown()

    @task
    def presentation_exchange(self):
        presentation = self.client.presentation_exchange(self.verifier_invite['connection_id'])


class Issue(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = between(float(os.getenv('LOCUST_MIN_WAIT',0.1)), float(os.getenv('LOCUST_MAX_WAIT',1)))
#    host = "example.com"

