# shinemonitor_api
Get info about your solar installation from ShineMonitor. REST-API with swagger using dotnet core with a python backend-backend.

Fill in user information in config.py. Either run the dotnet project to get a full Swaggger interface, or use the Python script i.e. ```python3 get_data.py``` If no arguments are provided to the script, it writes all information to a set of files. Or the flags ```--status```, ```--energyNow```, ```--energySummary``` or ```--energyTimeline``` can be used to only get specific information returned to console.