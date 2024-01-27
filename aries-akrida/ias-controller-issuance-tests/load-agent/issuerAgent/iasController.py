from .base import BaseIssuer
import json
import os
import requests
import time

class IasControllerIssuer(BaseIssuer):
        def issue_credential(self, did):
                print("**************IAS issue_credential***********")
                print(did)
                headers = {}
                headers["Content-Type"] = "application/json"
                headers["X-API-KEY"] = os.getenv("IAS_CONTROLLER_API_KEY")

                r = requests.post(
                        f"{os.getenv('IAS_CONTROLLER_URL')}/credentials/{did}/next",
                        headers=headers,
                )
                print("**************IAS issue_credential RESPONSE***********")
                print(r)
                if r.status_code != 200:
                        raise Exception(r.content)

                r = r.json()

                return {}