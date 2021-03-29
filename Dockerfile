# https://hub.docker.com/_/microsoft-dotnet
FROM mcr.microsoft.com/dotnet/sdk:5.0 AS build
WORKDIR /source

# copy csproj and restore as distinct layers
COPY *.csproj .
RUN dotnet restore

# copy and publish app and libraries
COPY src/ ./
RUN dotnet publish -c release -o /app --no-restore

# final stage/image
FROM mcr.microsoft.com/dotnet/aspnet:5.0
RUN apt-get update \
  && apt-get install -y python3 python3-pip \
  && pip3 install requests
WORKDIR /app
COPY src/get_data.py ./src/get_data.py
COPY src/config.py ./src/config.py
COPY --from=build /app .
EXPOSE 80
EXPOSE 443
EXPOSE 8000
EXPOSE 8001
ENTRYPOINT ["dotnet", "shinemonitor_api.dll"]