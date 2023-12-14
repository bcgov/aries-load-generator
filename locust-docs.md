# Load Testing Setup

See [Locust Video](https://www.loom.com/share/b52bd7c5e7ca4503951dffa1661b3bfa?sid=a9fe3330-397d-4e66-af99-86a0d4835068)

Components Needed:

- [Traction](https://github.com/bcgov/traction)
- [Mediator](https://github.com/hyperledger/aries-mediator-service)
- [AFJ](https://github.com/openwallet-foundation/agent-framework-javascript)
  - [Resolve Pickup Protocol](https://github.com/hyperledger/aries-akrida/blob/main/docs/NONCLUSTERED.md#resolving-pickup-protocol-versions)

The majority of the locust work will be based on [Aries Akrida](https://github.com/hyperledger/aries-akrida)
You can find majority of the setup here: [NonClustered Docs](https://github.com/hyperledger/aries-akrida/blob/main/docs/NONCLUSTERED.md#locust)

TLDR:

```
git clone git@github.com:hyperledger/aries-akrida.git
cd aries-akrida
git clone git@github.com:openwallet-foundation/agent-framework-javascript.git
```

Locust Docs Must Reads:

- [Tasks](https://docs.locust.io/en/stable/writing-a-locustfile.html#task-decorator)
- [Sequential Task Set](https://docs.locust.io/en/stable/tasksets.html#sequentialtaskset-class)

Once you've set up Locust you'll need to update the `.env` file:
See Traction/Mediator setup - once setup you should be ready to `docker-compose up`

Navigate to `localhost:8089` and enter `http://host.docker.internal:8032` as host. You should now be ready to execute the load test.

## Next steps involve:

- creating a new `pre-locust` script, for both setup and teardown.
  - the setup will include posting to setup the load test endpoints/configs specifications TBD
  - will use a multi use agent per connection
  - teardown endpoint will also be needed to be used.
- Creating a new Locust Behavoir.
  - Use the aries akrida base client, and create a new sequesntial task to request a credential locust mediator is an excellent example.

An Example API request file is below:

```
class UserBehaviour(SequentialTaskSet):
    def on_start(self):
         self.client.startup(withMediation=bool(WITH_MEDIATION))

    def on_stop(self):
         self.client.shutdown()

    @task
    def send_api_request_example(self):
        url = "https://swapi.dev/api/starships/9/"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            print("Name:", data["name"])
            print("Model:", data["model"])
        else:
            print("Failed to retrieve data from SWAPI")
```

### Common Issues

- docker caching issues.
  There are numerous docker volume/networking issues.

Some helpful commands:

- docker-compose down --volumes
- docker-compose down and then docker-compose up for env vars
- [Resolving Docker Port Issues](https://github.com/hyperledger/aries-akrida/blob/main/docs/NONCLUSTERED.md#resolving-docker-port-issues--hanging-docker)
- [WSL Relay Dead Port Issue](https://github.com/microsoft/WSL/issues/10601)
  - Task manager -> Details -> Look for `WSLRelay.exe` and kill it

### Traction & Mediator

1. register new user/wallet
1. connect to issuer/ledger
1. create cred def
1. get bearer token
1. get mediator url
1. sanity checks

Check if Acapy is available from the load agent:

`docker-compose exec load-agent curl -v http:/host.docker.internal:8032`

You should see something along the lines off:

```
PS C:\Users\yourname\aries-akrida> docker-compose exec load-agent curl -v http://host.docker.internal:8032/
time="2023-12-07T15:25:48-08:00" level=warning msg="The \"NODE_ENV\" variable is not set. Defaulting to a blank string."
*   Trying 192.168.65.254:8032...
* TCP_NODELAY set
* Connected to host.docker.internal (192.168.65.254) port 8032 (#0)
> GET / HTTP/1.1
> Host: host.docker.internal:8032
> User-Agent: curl/7.68.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 302 Found
< Server: nginx/1.24.0
< Date: Thu, 07 Dec 2023 23:25:48 GMT
< Content-Type: text/plain; charset=utf-8
< Content-Length: 10
< Connection: keep-alive
< Location: /api/doc
< Access-Control-Allow-Methods: GET, POST, OPTIONS, PUT, DELETE
< Access-Control-Allow-Credentials: true
<
* Connection #0 to host host.docker.internal left intact
302: Found
```
