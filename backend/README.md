# Backend

This directory contains the REST API server implementation for the ventilation control system. It handles communication between the hardware (OLIMEX A20 and MOD-IO) and the frontend, providing endpoints for status monitoring, configuration updates, and historical data retrieval.

## Technologies
- Python with Flask/FastAPI
- Integration with hardware scripts
- Database connectivity

## Key Components
- API endpoints for temperature monitoring and fan control
- Automatic mode logic based on temperature thresholds
- Manual override capabilities