# service-enterprise-ai


<!-- /TOC -->

This is backend of the Forestry Bureau project.

## Get started

## Prerequisites
- *service-enterprise-ai* are running in dockerized environment.
- Before starting please make sure [Docker CE](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/) are installed in your system.

## Initialization
Before you run the service, you need to set up your environment.
```cmd
./docker/run_init.sh
```

## Running

### Build service
```cmd
./docker/run_build_image.sh
```

### Start service
```cmd
./docker/run_service.sh
```

  After all services are successfully started, you can open http://{your-host-ip}:{service-port}/docs in you browser to know the information of the service (For example, http://127.0.0.1:8001/docs).

### Remove service
To stop and completely remove deployed docker containers:
```bash
./docker/docker-remove-service.sh
```

## Documentation
api file url: https://dev.azure.com/FET-IDTT/prod-ems-enterprise/_wiki/wikis/prod-ems-enterprise.wiki/2075/ems-ai-api-%E6%96%87%E4%BB%B6


## Version, author and other information
- See the relation information in [setup file](setup.py).

