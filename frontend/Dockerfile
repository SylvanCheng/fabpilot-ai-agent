# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY FabPilot.Web/FabPilot.Web.csproj FabPilot.Web/
RUN dotnet restore FabPilot.Web/FabPilot.Web.csproj
COPY FabPilot.Web/ FabPilot.Web/
RUN dotnet publish FabPilot.Web/FabPilot.Web.csproj -c Release -o /out --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /out .
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080
USER app
ENTRYPOINT ["dotnet", "FabPilot.Web.dll"]
