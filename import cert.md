# Install self-signed cert of Unciv_server
## Windows
You need to have the following folder structure:
```
\someFolder\Unciv-Windows64
\someFolder\Unciv_server
```
```
cd Unciv-Windows64
.\jre\bin\keytool -import -alias Unciv-server-cert -file "..\Unciv_server\localhost.crt" -keystore ".\jre\lib\security\cacerts" -noprompt -storepass changeit
```
## Linux
Tbd

## Mac
Tbd

## Android
Not possible
