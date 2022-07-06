# Server for Unciv written in Python

It's a simple webserver for Unciv that uses the Python built in http.server module.

## Installation

Make sure you have Python3 installed.
The server was tested with Python 3.7\3.8\3.9 and 3.10; Of course, we recommend Python 3.9 and 3.10

Use [git](https://git-scm.com) to download the Unciv_server

```bash
git clone https://github.com/Mape6/Unciv_server.git
cd Unciv_server
```

## Usage

```
usage: Unciv_server.py [-h] [-p PORT] [-g] [-l {CRITICAL,ERROR,WARNING,INFO,DEBUG}] [-s] [--pub-cert PUB_CERT] [--prv-key PRV_KEY]

This is a simple HTTP webserver for Unciv

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Specifies the port on which the server should listen (default: None)
  -g, --game-logfiles   Writes separate logfiles for each game
  -l {CRITICAL,ERROR,WARNING,INFO,DEBUG}, --log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}
                        Change logging level (default: WARNING)
  -s, --ssl             Starts a HTTPS server instead of HTTP
  --pub-cert PUB_CERT   Set name of public certificate file
  --prv-key PRV_KEY     Set name of private key file
```

To start an HTTPS server on the default port 443 with a certificate named localhost.crt and a private key named localhost.key:
```
python Unciv_server.py -s --pub-cert localhost.crt --prv-key localhost.key
```

The SSL support is very rudimentary and the certificate is self-signed. Don't make the server directly reachable from the internet.
I strongly recommend to use a reverse proxy in front of this webserver to take care of the certificate and termination of the SSL sessions.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
This project is [MPL-2.0](https://github.com/Mape6/Unciv_server/blob/main/LICENSE) licensed.
