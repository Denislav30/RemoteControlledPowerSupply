# Database

This directory contains the database schema, migration scripts, and data persistence layer for the ventilation control system. It uses SQLite for lightweight, embedded database functionality suitable for the OLIMEX A20 environment.

## Contents
- Database schema definitions
- Migration scripts
- Data models and ORM configurations
- Backup and restore utilities

## Tables
- `config`: System configuration and thresholds
- `logs`: Temperature readings and fan events
- `system_health`: System status and error logs