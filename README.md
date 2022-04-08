# Server for Unciv written in Python

It's a simple webserver for Unciv that uses the Python built in http.server module.

## Installation

Make sure you have Python3 installed.
The server was tested with Python 3.9 and 3.10.

Use [git](https://git-scm.com) to download the Unciv_server

```bash
mkdir Unciv_server
cd Unciv_server
git pull https://github.com/Mape6/Unciv_server.git
```

## Usage

```
usage: Unciv_server.py [-h] [-p PORT] [-v]

This is a simple HTTP webserver for Unciv

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  specifies the port on which the server should listen (default: 80)
  -v, --verbose         change logging level to INFO (default: WARNING)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
This project is [MPL-2.0](https://github.com/Mape6/Unciv_server/blob/main/LICENSE) licensed.
