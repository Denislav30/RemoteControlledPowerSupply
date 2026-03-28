# Remote Controlled Ventilation System

**Course Project: Distributed Embedded Systems**

A comprehensive ventilation control system that automatically regulates room temperature using an OLIMEX A20 single-board computer and MOD-IO expansion module. The system features real-time temperature monitoring, automated fan control based on configurable thresholds, and a web-based dashboard for remote monitoring and manual override.

## Features

- **Real-time Temperature Monitoring**: Analog thermometer connected to MOD-IO's ADC for accurate temperature readings
- **Automated Fan Control**: Relay-controlled ventilation system with automatic activation based on temperature thresholds
- **REST API Backend**: Python-based server running on OLIMEX A20 for system control and data management
- **Web Dashboard**: Responsive frontend for remote monitoring and manual control from phones or PCs
- **Database Integration**: SQLite database for storing configuration, logs, and historical data
- **Safety Features**: Hardware-level emergency controls and system health monitoring

## Architecture

The system consists of four main components:

- **Hardware Layer** (`hardware/`): Low-level scripts for ADC readings, relay control, and I2C communication
- **Backend API** (`backend/`): REST server handling business logic, automatic control, and data persistence
- **Database** (`database/`): Schema and persistence layer for configuration and logs
- **Frontend** (`frontend/`): Web interface for user interaction and real-time monitoring

## Hardware Requirements

- OLIMEX A20 single-board computer
- MOD-IO expansion module
- Analog temperature sensor
- Relay-controlled fan system
- Voltage divider circuit for ADC input

## Usage

1. Start the backend server on A20
2. Access the web dashboard from any device
3. Configure temperature thresholds
4. Monitor real-time data and control manually if needed

## API Documentation

See `docs/` directory for detailed API specifications and endpoint documentation.

## Team

- **Kristian**: Hardware setup and low-level drivers
- **Elena**: Backend REST API development
- **Ivailo**: Database design and persistence
- **Denislav**: Frontend web dashboard

## Project Status

This is an active development project for the Distributed Embedded Systems course.
