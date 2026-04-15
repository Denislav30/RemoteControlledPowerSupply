Kristian
    [DONE] 1. Flash a SD Card for Olimex A20 with appropriate Linux distribution (e.g., Debian or Ubuntu for ARM).
            [NOTE] Operating system is flashed on a SD card and it was successfully lauched on the A20
    [DONE] 2. Setup, Update and test the A20 board (install necessary packages, configure network, SSH access).
            [NOTE] Board was connected to Ethernet and all local packs were updated.
            [NOTE] Added SSH login.
            [NOTE] Installed Python.
    [DONE] 3. Connect MOD-IO to A20 via UEXT interface and verify connection.
            [NOTE] The controller was connected through UETX and it was tested throught the Relays
    [DONE] 4. Setup, update and test ADC and Relay functionality via UEXT communication using appropriate libraries (e.g., smbus for Python).
            [NOTE] smbus was installed and tests for reading the ADCs.
    [DONE] 5. Setup the analog thermometer and calibrate ADC values to temperature readings (Celsius/Fahrenheit) - create calibration script.
            [NOTE] Analog Thermometer is behaving strange at the moment. The readings are a bit low...
    [DONE] 6. Setup the Fan system (relay-controlled) and ensure physical connectivity and power supply.
            [NOTE] Tested with a single 12V FAN with an external Power Supply.
            [NOTE] Test was successful, sadly the external supply cna handle single fan only
    [DONE] 7. Develop low-level scripts/drivers to expose hardware readings (temperature, fan state) to the Backend.
            [WIP] Reading for all ADCs. Both continuous and Single read.
            [WIP] Reading for all Digital Inputs (IN0-IN3). Both continuous and Single.
            [WIP] Writing for All Digital Outputs (OUT0-OUT3) 
    [DONE] 8. Setup the Voltage divider circuit for ADC input and verify correct voltage readings.
            [NOTE] Circuit is working correctly and it is documented.
            [NOTE] Tested different configurations with different input Voltages.
    [DOME] 9. Implement hardware-level safety checks (e.g., emergency fan activation on high heat thresholds).
    [KINDA-DONE] 10. Document hardware setup procedures and troubleshooting steps.
---------------------------------------------------------------------------------------
Elena
[Done]  1. Design and implement the REST API on the A20 (using Flask, FastAPI, or Express) - choose based on performance and ease of deployment.
[DONE]  2. Implement logic for "Automatic" mode: Fan control based on temperature vs. stored thresholds (polling or interrupt-based).
        3. Create API endpoints for:
[DONE]          - GET `/api/status`: Current temperature, fan state, mode, and system health.
[DONE]          - POST `/api/settings`: Update temperature thresholds, manual/auto mode, and other config.
[]              - GET `/api/history`: Retrieve historical temperature data from DB with pagination.
[DONE]          - POST `/api/manual-control`: Override fan state manually.
[]              - Implement Voltage threshhold.
[WIP]   4. Integrate hardware scripts provided by Kristian into the API service (handle UEXT communication securely).
[]      5. Implement error handling, logging, and basic authentication for API security.
[]      6. Add API documentation (e.g., using Swagger/OpenAPI).
[DONE]  7. Create Dummy modules for unit testing.
[]      8. Unit tests.
---------------------------------------------------------------------------------------
Ivailo
         1. Design Database schema (SQLite recommended for A20 environment):
                - Table `config`: Store thresholds (min_temp, max_temp), mode (auto/manual), fan_override.
                - Table `logs`: Store periodic temperature readings (timestamp, temp), fan toggle events (timestamp, state, reason).
                - Table `system_health`: Store system status and error logs.
         2. Implement data persistence layer for the Backend (ORM or direct SQL queries).
         3. Sync with Denislav to ensure data structure supports frontend graphs/history (e.g., time-series data).
         4. Implement database migrations and backup/restore functionality.
[Prio 3] 5. Optimize database for low-resource environment (A20 constraints).
---------------------------------------------------------------------------------------
Denislav
    1. Design and develop a responsive Web Dashboard (React, Vue.js or similar) for mobile and desktop.
    2. Implement real-time data polling (or WebSockets) for temperature monitoring and status updates.
    3. Create UI controls for:
        - Manual fan override toggle.
        - Threshold adjustment forms with validation.
        - Mode switch (auto/manual).
        - Historical data charts/graphs.
    4. Implement user authentication and session management if needed.
    5. Ensure cross-browser compatibility and mobile responsiveness.
    6. Add notifications for alerts (e.g., high temperature warnings).
---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------

General/Integration Tasks
    1. Define project requirements and specifications document.
    2. Setup version control and CI/CD pipeline for automated testing and deployment.
    3. Conduct integration testing: Hardware + Backend + DB + Frontend.
    4. Implement monitoring and logging across all components.
    5. Create user documentation and deployment guide.
    6. Security review: Ensure secure communication, input validation, and access controls.
    7. Performance testing under various temperature conditions.
    8. Backup and recovery procedures for data and configurations.
