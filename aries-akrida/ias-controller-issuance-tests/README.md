# IAS Test Issuer Load Testing

Minor note: do we like "IAS" or "IDIM" for labelling the load testing and stuff we do here?

This folder contains the work-in-progress changes to the Akrida framework (https://github.com/hyperledger/aries-akrida), and design/running notes needed for the planned load testing excercises with the IAS Test Issuer for the Person Credential.

The Load Testing plan is documented here:
https://ditp-bc.atlassian.net/wiki/spaces/DESIGN/pages/106070023/Person+Credential+Load+Testing+Design

This doesn't contain any details on that IAS Test Issuer controller, just the changes needed for an Aries Akrida framework to run against that controller to issue creds to the local Akrida-created AFJ agents.

## Akrida Changes Required

A number of changes are needed to fit the IAS test case into the existing Akrida flow.

The files in Akrida/AFJ modified locally to make this work are contained in this repository. Any files found (under this top level `ias-controller-issuance-tests` folder) can be copied into a cloned Aries Akrida project in the same directory structure here (or for .env add the 4 relevant keys to a sample env file).

### .env and docker-compose.yml
Need to change `LOCUST_FILES` to use the included which flavor of the new `locustMediatorIasIssue.py` file to use. See details of each below.

Set `LEDGER` to bcovrin or candy depending on use case. (Check with IDIM which environment/ledger combo)

Some new environmnent variables need to be added for the IAS API calls as well.

The new environment variables need to be added to the docker compose as well so they get imported.

### locustMediatorIasIssue*.py
The locust test to run to do the issuance, customized for the IAS use case being tested here.
Based on `locustMediatorIssue.py` originally. Relevant changes described for each one below.

- Modified to recieve a provided invitation url (Connections protocol) that is given in ENV file.
- Modified to call a custom issuerAgent that invoked the IAS controller to do the issuance.

There are 3 versions of the script included here.

#### locustMediatorIasIssue.py
- For a User does the receive invite, call for cred issuance, recieve cred just once and then is done.
- Need a dummy empty task to not throw an error.

#### locustMediatorIasIssueSingleInvitation.py
- Gets an invitation at the beginning of the user flow
- Then runs the task receiveing a credential to that DID repeatedly

#### locustMediatorIasIssueDeleteReuseInvitation.py
- Gets an invitation at the beginning of each repeated task and recieves the credential
- Then DELETES the OOB record (aries errors if it tries to recieve the invite again)
- So on next @task run it recieves the invite again and recieves a cred again
- Runs the task a total of 10 times per use (TODO to parameterize this). Take out the counter check if you want it to keep repeating

### agent.ts
The AFJ Agent invocation needs to be changed here. The IAS Controller needs a connection DID for the issuance call. The Akrida tests were only returning an OOB object, not the connection with the DID.

Then the DID from that connection result in AFJ is a Peer DID and that needs to be converted to a legacy DID in order for the IAS controller to be able to use it successfully. The code to do this (below) was just lifted from the BC Wallet source code.

```
    // LO: retrieve the legacy DID. IAS controller needs that to issue against
    // This code adapted from https://github.com/bcgov/bc-wallet-mobile/blob/main/app/src/helpers/BCIDHelper.ts
    const legacyDidKey = '_internal/legacyDid' // TODO:(from BC Wallet code) Waiting for AFJ export of this.
    const didRepository = agent.dependencyManager.resolve(DidRepository)  
    const dids = await didRepository.getAll(agent.context)
    const didRecord = dids.filter((d) => d.did === connectionRecord?.did).pop()
    legacyConnectionDid = didRecord.metadata.get(legacyDidKey)!.unqualifiedDid
```

Added a `deleteConnectionById` function that deletes an oob record. This just invokes the call down to AFJ `agent.oob.deleteById` but doesn't do event waiting the way some of the other ones in here do... seems to work but a TODO to see if this should be changed.

### locustClient.py
Add a call to the new delete OOB record function

### iasController.py
This file just makes the appropriate API call to the IAS controller to invoke issuance to the supplied DID.

## Running Tests
**Before running any tests confirm with the appropriate people at IDIM. Alwyas make sure the DELETE endpoint to clean up tests is run after. Do not do any large load when testing out changes**

### Akrida set up
1. Clone the aries Akrida repo
2. Within the root aries-akrida folder, clone Agent Framework JavaScript (`git clone https://github.com/openwallet-foundation/agent-framework-javascript`)
1. Modify the relevant files locally by overwriting with the changes contained here. (do `.env` after the next step, just adding the keys contained in the .env here)
1. Copy `sample.env` to the same location, rename as `.env`

### IAS Controller setup
1. Figure out which environment to work against. Get the URLS and the API Key for that env and the structure for the API calls. Can be found on confluence page.
1. POST to `vc-test/load-tests?workers=n` and get the invitation URL.
1. Record the alias
1. After tests are over ensure you run DELETE `vc-test/load-tests/{alias}`

### Environment
1. In the `.env` file set the invitation URL and IDIM controller API details. These are the new environment vars desribed above.
2. Set `LOCUST_FILES=locustMediatorIasIssue.py`

### Build/run
1. In the root, run `docker compose build`
2. Start the framework with `docker compose -f docker-compose.yml up -d`
3. Monitor logs with `docker compose -f docker-compose.yml logs -f`
4. Go to the test dashboard at http://localhost:8089
5. Start a small test 
6. When ready, click "Stop Test"
7. Run `docker compose -f docker-compose.yml stop` to stop the swarm.

## Notes/TODOs
- Some of the things in here, specifically the `agent.ts` changes are now specifying the tests to the IAS test case here. Need to generalize some more before commiting back to Akrida
- Need more testing out/hardening. Sometimes I get a 404 on the first cred issuance back from the IAS controller, may be a timing thing. (Update: I added a 1 second wait before calling issue, no more 404s so far...)