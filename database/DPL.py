import sqlite3
import shutil
import os
from datetime import datetime

DB_NAME = "database.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temperature REAL,
        fan1 INTEGER,
        fan2 INTEGER,
        fan3 INTEGER,
        reason TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_health (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voltage REAL,
        fan_power_ok INTEGER,
        hw_error INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        threshold1 REAL,
        threshold2 REAL,
        threshold3 REAL,
        hysteresis REAL,
        mode TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO config (threshold1, threshold2, threshold3, hysteresis, mode)
    SELECT 28, 30, 32, 0.5, 'AUTO'
    WHERE NOT EXISTS (SELECT 1 FROM config)
    """)

    conn.commit()
    conn.close()


#LOGS
def insert_log(temp, fans, reason):
    if len(fans) != 3:
        raise ValueError("Fans must be list of 3 values")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO logs (temperature, fan1, fan2, fan3, reason)
    VALUES (?, ?, ?, ?, ?)
    """, (temp, int(fans[0]), int(fans[1]), int(fans[2]), reason))

    conn.commit()
    conn.close()


def get_logs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    data = cursor.fetchall()

    conn.close()
    return data


#SYSTEM HEALTH
def insert_health(voltage, fan_power_ok, hw_error):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO system_health (voltage, fan_power_ok, hw_error)
    VALUES (?, ?, ?)
    """, (voltage, int(fan_power_ok), int(hw_error)))

    conn.commit()
    conn.close()


def get_health():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM system_health ORDER BY timestamp DESC")
    data = cursor.fetchall()

    conn.close()
    return data


#CONFIG
def get_config():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM config LIMIT 1")
    data = cursor.fetchone()

    conn.close()
    return data


def update_config(t1, t2, t3, hysteresis, mode):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE config
    SET threshold1 = ?, threshold2 = ?, threshold3 = ?, hysteresis = ?, mode = ?
    WHERE id = 1
    """, (t1, t2, t3, hysteresis, mode))

    conn.commit()
    conn.close()

#RESTORE & BACKUP TBD
