# Semester Project of Group 7 - Desk Booking System

## Run the Application
Before running the application, make sure to create a `.env` file in the root directory of the project with the necessary environment variables. It should contain the following variables:

```env
BOOKING_DB_USER=<user>
BOOKING_DB_PASS=<password>
BOOKING_DB_NAME=<database>

INVENTORY_DB_USER=<user>
INVENTORY_DB_PASS=<password>
INVENTORY_DB_NAME=<database>

USER_DB_USER=<user>
USER_DB_PASS=<password>
USER_DB_NAME=<database>

OCCUPANCY_DB_USER=<user>
OCCUPANCY_DB_PASS=<password>
OCCUPANCY_DB_NAME=<database>

PGADMIN_EMAIL=<email>
PGADMIN_PASSWORD=<password>
```
Replace `<user>`, `<password>`, `<database>`, and `<email>` with the appropriate values for your PostgreSQL and pgAdmin instances.


To run the entire application with all services, use the following command in the root directory of the project:
```bash
docker-compose up -d
```
This will start all the services defined in the `docker-compose.yml` file.

To stop the running containers, use the command:
```bash
docker-compose down
```

## CI Pipeline
This project uses GitHub Actions for continuous integration (CI). The CI pipelines are defined in the `.github/workflows/ci-*.yml` files.
It includes steps for building the application, running tests, and checking code quality.

| Service | CI |
|---|---|
| Booking Service | [![CI Booking Service](https://github.com/44sven/sepro-group-7/actions/workflows/ci-booking.yml/badge.svg)](https://github.com/44sven/sepro-group-7/actions/workflows/ci-booking.yml) |
| Desk Integration Service | [![CI Desk Integration Service](https://github.com/44sven/sepro-group-7/actions/workflows/ci-desk-integration.yml/badge.svg)](https://github.com/44sven/sepro-group-7/actions/workflows/ci-desk-integration.yml) |
| Desk Inventory Service | [![CI Desk Inventory Service](https://github.com/44sven/sepro-group-7/actions/workflows/ci-desk-inventory.yml/badge.svg)](https://github.com/44sven/sepro-group-7/actions/workflows/ci-desk-inventory.yml) |
| Gateway | [![CI Gateway](https://github.com/44sven/sepro-group-7/actions/workflows/ci-gateway.yml/badge.svg)](https://github.com/44sven/sepro-group-7/actions/workflows/ci-gateway.yml) |
| Occupancy Service | [![CI Occupancy Service](https://github.com/44sven/sepro-group-7/actions/workflows/ci-occupancy.yml/badge.svg)](https://github.com/44sven/sepro-group-7/actions/workflows/ci-occupancy.yml) |
| User Service | [![CI User Service](https://github.com/44sven/sepro-group-7/actions/workflows/ci-user.yml/badge.svg)](https://github.com/44sven/sepro-group-7/actions/workflows/ci-user.yml) |
[![CI Scheduler Service](https://github.com/44sven/sepro-group-7/actions/workflows/ci-scheduler-service.yml/badge.svg?branch=main)](https://github.com/44sven/sepro-group-7/actions/workflows/ci-scheduler-service.yml)




## Code Coverage
This project uses Codecov to track code coverage. After running tests, coverage reports are generated and
uploaded to Codecov for analysis. The code coverage only includes all microservices and not the frontend. The overall code coverage can be seen below:

[![codecov](https://codecov.io/github/44sven/sepro-group-7/graph/badge.svg?token=TRH1NWB1KC)](https://codecov.io/github/44sven/sepro-group-7)