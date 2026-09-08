# src/<AppName>.Server/Dockerfile
#
# Build context is the REPOSITORY ROOT, not src/ — the restore layer needs
# Directory.Build.props from the root, and a Dockerfile can only COPY from
# within its context. The docker-release workflow passes `context: .` for this
# reason; building with `docker build src/` will fail on the first COPY.
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /build

# --- Restore layer ---------------------------------------------------------
# Copy only the version file and the .csproj/.sln files first, restore, and
# only then copy the source. Docker caches layers by content, so an ordinary
# code change reuses the (slow) restore layer instead of re-downloading every
# package. Adding a project means adding its COPY line here.
COPY Directory.Build.props .
COPY src/<AppName>.sln src/
COPY src/<AppName>.Shared/<AppName>.Shared.csproj src/<AppName>.Shared/
COPY src/<AppName>.Client/<AppName>.Client.csproj src/<AppName>.Client/
COPY src/<AppName>.Server/<AppName>.Server.csproj src/<AppName>.Server/
RUN dotnet restore src/<AppName>.Server/<AppName>.Server.csproj

COPY . .
RUN dotnet publish src/<AppName>.Server/<AppName>.Server.csproj -c Release -o /app/publish

# --- Runtime layer ---------------------------------------------------------
# aspnet, not sdk: the runtime image is a fraction of the size and carries no
# compiler for an attacker to reach.
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime

# Native tools the app shells out to. Install them here rather than assuming
# the host has them, and clean the apt lists in the same RUN so the cache
# doesn't end up baked into the layer.
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends <packages> \
#     && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=build /app/publish .

# Fixed internal port; the host port is chosen by compose (APP_PORT).
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080

ENTRYPOINT ["dotnet", "<AppName>.Server.dll"]
