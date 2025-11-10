## Project: Monitoring DOS Or DDOS on specific PORT

- This project intends to limit number of connections that can be made to a specific port per specific ip address to avoid denial of service

### Installation
` Install python already installed in linux or download it from https://www.python.org/downloads for windows`
### Setup virtual environment and install the following packages
- python -m venv .venv
- source .venv/bin/activate  # on Windows: .venv\\Scripts\\activate
- pip install -r requirements.txt

The requirements include:
- psutil
- scapy
- Flask (web API)
- pymongo (MongoDB driver)
- python-dotenv (load settings from .env)

## Usage
### Run sample HTTP server (for generating connections)
- Run python3 -m http.server [this will run on port 8000]
- Open localhost:8000 in browser and keep refreshing to create more connections

### Run Flask API with MongoDB support
1. Ensure MongoDB is running locally or set MONGODB_URI in .env
2. Create a .env file in the project root with any of the following (optional):
   - MONGODB_URI=mongodb://localhost:27017
   - MONGODB_DB=monitordos
   - MONGODB_COLLECTION=events
   - FLASK_HOST=0.0.0.0
   - FLASK_PORT=5000
   - FLASK_DEBUG=true
3. Start the API:
   - python app.py
4. Test endpoints:
   - GET http://localhost:5000/health
   - POST http://localhost:5000/events (JSON body)
   - GET http://localhost:5000/events
   - Swagger UI: http://localhost:5000/api/swagger

### Block detected attacking IP address
`In linux: iptables -A INPUT -s <ip> -j DROP`
### Unblocking blocked attacking IP address
`In linux: iptables -D INPUT -s <ip> -j DROP`

### Setup global libs to monitor process and save logs
`sudo pip install psutil python-dotenv pymongo`
### Run DOS Detection script
`sudo python3 active_connection.py`

### Run Website monitoring script
`sudo python3 monitor_web.py`

