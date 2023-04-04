# shinemonitor_api
Get info about your solar installation from ShineMonitor. REST-API with swagger using Dotnet Core with a Python backend-backend.

First install python requests with `python3 -m pip install requests`.

Fill in user information in config.py. The Python script is the part actually calling the Shinemonitor web. Use it standalone with ```python3 get_data.py```. If no arguments are provided to the script, it writes all information to a set of files. The flags ```--status```, ```--energyNow```, ```--energySummary``` or ```--energyTimeline``` can be used to only get specific information returned to console.

To run the REST-API project, first create a Https development certificate (https://docs.microsoft.com/en-us/aspnet/core/security/docker-https?view=aspnetcore-5.0).

To run the API locally, use ```dotnet build``` and ```dotnet run```. The Swagger interface should now be accessible at https://localhost:5001.

To use docker, use docker-compose with ```docker-compose build``` and ```docker-compose up```. The Swagger interface should now be accessible at https://localhost:8001