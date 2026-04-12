Here is a formal, professionally structured `README.md` documentation for your project. It is designed to be accessible to non-technical users while maintaining the professional tone required for a hardware-software integration project.

---

# System Documentation: Olimex A20 Staged Cooling Controller

## 1. Project Overview
The **Olimex A20 Staged Cooling System** is an integrated hardware and software solution designed to provide automated thermal management for indoor environments. By utilizing an Olimex A20 microcomputer and a MOD-IO expansion board, the system monitors environmental temperatures and activates a three-stage cooling response. This approach optimizes energy efficiency, reduces mechanical wear on hardware, and minimizes ambient noise.

---

## 2. Functional Description

### 2.1 Automated Cooling (Staged Logic)
The system operates primarily in **Automatic Mode**. In this state, the software manages three independent fans based on predefined temperature thresholds:
* **Stage 1:** Activates Fan 1 when the temperature reaches **28.0°C**.
* **Stage 2:** Activates Fan 2 when the temperature reaches **30.0°C**.
* **Stage 3:** Activates Fan 3 when the temperature reaches **32.0°C**.

To prevent "relay chattering" (rapid switching caused by minor temperature fluctuations), a **0.5°C Hysteresis** is applied. This means a fan activated at 28.0°C will remain active until the temperature drops below 27.5°C.

### 2.2 Control Modes
* **Automatic Mode:** Indicated by a **Logical High (LED ON)** on the hardware. The system logic holds total priority.
* **Manual Mode:** Indicated by a **Logical LOW (LED OFF)**. Control is ceded to the user via the web interface. Users may toggle individual fans regardless of current temperature.

---

## 3. Safety and Health Monitoring

### 3.1 Hardware Watchdog (Safe State)
The system continuously monitors the communication link between the software and the hardware controllers. If a communication failure is detected (e.g., a disconnected cable or script error), the system enters a **Safe State**, immediately activating all three fans to ensure the environment does not overheat during the fault.

### 3.2 Power Supply Supervision
Through the Analog-to-Digital Converter (ADC), the system monitors the 12V power rail dedicated to the fans. 
* If the system attempts to activate a fan but detects a voltage drop below **10V**, a **Critical Power Alert** is triggered on the dashboard.

---

## 4. User Interface Guide

### 4.1 Authentication
Access to system controls (Mode toggling, Manual Fan control, and Threshold adjustment) is restricted. 
* **Default Credentials:** `admin` / `admin`
* **Session Management:** Security is handled via JSON Web Tokens (JWT). Sessions expire after 60 minutes of inactivity.

### 4.2 Dashboard Indicators
| Element | Description |
| :--- | :--- |
| **🌀 Icon** | Indicates the fan is receiving a "Run" command. |
| **⚪ Icon** | Indicates the fan is in an "Idle" state. |
| **Temp Display** | Real-time ambient temperature from the ADC1 sensor. |
| **Status Badge** | Displays current operational mode (Auto/Manual) or system errors. |

---

## 5. Hardware Interconnect (UEXT)
For technical reference, the system utilizes the following pin mapping on the MOD-IO board:

* **Digital Output 1:** Mode Status Indicator (LED).
* **Digital Output 2-4:** Fan Relays 1, 2, and 3.
* **Analog Input 1:** Precision Temperature Sensor.
* **Analog Input 2:** Fan Power Supply Voltage Monitor.

---

## 6. Maintenance and Alerts
Users should attend to the following alerts if they appear on the dashboard:
* **CRITICAL POWER FAILURE:** Verify the external 12V power supply connection.
* **HW DISCONNECT:** Inspect the UEXT cable connection between the Olimex A20 and the MOD-IO board.

---

**Document Version:** 1.0.2  
**Hardware Platform:** Olimex A20-OLinuXino-LIME2  
**Expansion:** MOD-IO (Relay/ADC/DIN)