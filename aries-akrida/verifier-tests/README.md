TBD

Notes: 
Should merge in https://github.com/hyperledger/aries-akrida/pull/45 if that is sorted so we don't need those changes here. If not will need those fixes applied to local.



### locustMediatorVerifier.py
Uses a Traction instance (Sandbox)

On startup, single time per user,
- Create invitation through issuer Traction agent
- Accept that with local agent
- Issue cred through Traction agent and receive it
- Create invitation through verifier Traction agent
- Accept that with local agent

Then the repeating `presentation_exchange` step invokes the verifier Traction agent `/present-proof/send-request`


### locustMediatorVerifierPersonCred.py
...

### locustMediatorVerifierVcauthn.py
...