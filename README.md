# shinemonitor_api
Get info about your solar installation from ShineMonitor. The project is a python FastAPI application that provides an REST-API to interact with Shinemonitor. 

## Setup Instructions
### 1. Create a virtual environment
```
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Run the application
```
uvicorn src.main:app --reload
```

### Docker
```
docker-compose build
docker-compose up -d
```

The Swagger interface should now be accessible at https://localhost:8000/swagger

## Usage
Once the application is running, you can access the following endpoints:

- **Get Status:** `/status`
- **Get Energy Now:** `/now`
- **Get Energy Summary:** `/summary`
- **Get Energy Timeline:** `/timeline`

## Config parameters
### Username and Password
- Note that both username and password must be URL encoded (https://www.w3schools.com/tags/ref_urlencode.ASP)

### Company key
- Go to your web portal provider at \<provider\>.shinemonitor.com
- Open up devtools in chrome or web inspector in safari
- Inspect the source and find your 'company-key=\<company key\>'

### Plantid (Power station ID)
- Log in to your web portal provider
- Open up devtools in chrome or web inspector in safari
- Inspect the network requests, find the one with 'action=queryPlantInfo' and get your 'plantid=\<plant id\>' number

### Pn (Datalogger PN number)
- Log in to your web portal provider
- Open up devtools in chrome or web inspector in safari
- Inspect the network requests, find the one with 'action=queryTodayDevicePvCharts' and get your 'pns=\<pn number\>' number

### Sn (Device serial number)
- Log in to your web portal provider
- Open up devtools in chrome or web inspector in safari
- Inspect the network requests, find the one with 'action=queryTodayDevicePvCharts' and get your 'sns=\<serial number\>' number

### Devcode (Device coding)
- Log in to your web portal provider
- Open up devtools in chrome or web inspector in safari
- Inspect the network requests, find the one with 'action=queryTodayDevicePvCharts' and get your 'devcodes=\<device code\>' number
