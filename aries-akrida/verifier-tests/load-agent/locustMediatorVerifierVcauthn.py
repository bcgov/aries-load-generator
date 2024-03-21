from locust import SequentialTaskSet, task, User, between
from locustClient import CustomClient
import time
import inspect
import json
from bs4 import BeautifulSoup
import base64

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


    def on_stop(self):
        self.client.shutdown()

    @task
    def get_vcauth_presentation(self):
        # Go to the landing page/login redirect for whatever app is authing with VCauthn (or direct to VCauthn?)
        # Get the deep link from the page, and decode that pres exch

        # TODO: parameterize this URL
        response = self.client.get("https://a2a-dev.apps.silver.devops.gov.bc.ca/landing?kc_idp_hint=verifiable-credential", allow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        deep_link = soup.find(id="deep-link-button")    
        if deep_link is not None:
            href = deep_link.get('href')
            c_i = href.split("?c_i=")[1]

            decoded_bytes = base64.b64decode(c_i)
            json_string = decoded_bytes.decode('utf-8')
            json_dict = json.loads(json_string)
            print(f"DEBUG: deep_link decoded: {json_string}")
            self.vcauth_pres = json_dict
        else:
            print("No deep link found")  
            # todo fail the test here

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

