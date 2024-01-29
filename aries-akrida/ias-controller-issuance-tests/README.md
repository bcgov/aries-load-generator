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
Need to change `LOCUST_FILES` to use the included new `locustMediatorIasIssue.py` file.
Some new environmnent variables need to be added for the IAS API calls as well.

The new environment variables need to be added to the docker compose as well so they get imported.

### locustMediatorIasIssue.py
The locust test to run to do the issuance, customized for the IAS use case being tested here.
Based on `locustMediatorIssue.py` originally. Relevant changes described below:

- The other issuance tests in Akrida spin up an agent and then recieve an invitation every time it runs throuhg the test on the agent. Not sure how this ever works on other tests? Errors when trying to recieve the same invitation on the same agent a second time (maybe different invitation type on other Akrida tests?), but regardless, modified to recieve the invitation once at the beginning.
- Modified to recieve a provided invitation url (Connections protocol) that is given in ENV file.
- Modified to call a custom issuerAgent that invoked the IAS controller to do the issuance.

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

### iasController.py
This file just makes the appropriate API call to the IAS controller to invoke issuance to the supplied DID.


### BaseAgent.ts
Akrida just uses the AFJ demo source to start up agents, this contains the BCOVRIN-TEST genesis for ledger. We want to use Candy, so need to add that.
Must be a better way of doing this than relying on the demo...?

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
- The tests recieve a credential and complete but overall mark it as a failure with a `Exception(b'')` message. TODO to figure out where it's not capping off the test to mark as success.
- Need more testing out/hardening. Sometimes I get a 404 on the first cred issuance back from the IAS controller, may be a timing thing.