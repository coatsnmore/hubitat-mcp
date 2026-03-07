@echo off
set TAG=0.0.1

docker build -t coatsnmore/hubitat-mcp:%TAG% .
docker push coatsnmore/hubitat-mcp:%TAG%
