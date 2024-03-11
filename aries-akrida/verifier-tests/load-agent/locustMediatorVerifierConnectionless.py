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

        # Create a connectionless request
        connectionless = self.client.verifier_connectionless_request()
        print(f"DEBUG: PR result: {connectionless}")

    def on_stop(self):
        self.client.shutdown()

    @task
    def presentation_exchange(self):
        # TODO: Implement the functionality to have Credo accept the connectionless request,
        # do the verification, and then have the verifier verify it completed
        # I think this needs a new client/agent/whatever functions to be created calling the appropriate
        # Credo APIs
        pass


class Issue(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = between(float(os.getenv('LOCUST_MIN_WAIT',0.1)), float(os.getenv('LOCUST_MAX_WAIT',1)))
#    host = "example.com"

