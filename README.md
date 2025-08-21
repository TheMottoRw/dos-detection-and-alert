## Project: Monitoring DOS Or DDOS on specific PORT

- This project intends to limit number of connections that can be made to a specific port per specific ip address to avoid denial of service

### Installation
` Install python already installed in linux or download it from https://www.python.org/downloads for windows`
### Setup virtual environment and install the following package
- pip install psutil
- pip install scapy

## Usage
- Run python3 -m http.server [this will run on port 8000]
- Open localhost:8000 in browser and keeps refreshing to create more connections
### Block detected attacking ip address
`In linux: iptables -A INPUT -s <ip> -j DROP`
### Unblocking blocked attacking ip address
`In linux: iptables -D INPUT -s <ip> -j DROP`

