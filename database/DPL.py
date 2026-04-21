import sqlite3
import os
import hmac
import hashlib
from datetime import datetime

DB_NAME = "database.db"
HMAC_KEY = b"nsshmack"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;") #change to WAL for faster and safer writes
    conn.execute("PRAGMA synchronous=NORMAL;") #changed to NORMAL for better performance 
    return conn

def generate_hmac(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    return hmac.new(HMAC_KEY, data, hashlib.sha256).hexdigest() #generate HMAC signature 

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
        reason TEXT CHECK(length(reason) <= 70), /*limit reason to 70 chars because of database overflow*/
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

    cursor.execute("""  /*Insert default config*/
    INSERT INTO config (threshold1, threshold2, threshold3, hysteresis, mode)
    SELECT 28, 30, 32, 0.5, 'AUTO'
    WHERE NOT EXISTS (SELECT 1 FROM config)
    """)

    #create indexes for faster queri sorting 
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_time ON logs(timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_health_time ON system_health(timestamp);")

    conn.commit()
    conn.close()

def insert_log(temp, fans, reason):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO logs (temperature, fan1, fan2, fan3, reason)
        VALUES (?, ?, ?, ?, ?)
        """, (temp, int(fans[0]), int(fans[1]), int(fans[2]), reason))

        cursor.execute("""
        DELETE FROM logs 
        WHERE timestamp <= datetime('now', '-7 days') /*keep only 7 days of logs to keep the DB fresh*/
        """)

        conn.commit()
    finally:
        conn.close()


def get_logs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM logs 
    ORDER BY timestamp DESC 
    LIMIT 300 /*limit to 300 logs to avoid overloading the UI*/
    """)

    data = cursor.fetchall()
    conn.close()
    return data

def insert_health(voltage, fan_power_ok, hw_error):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO system_health (voltage, fan_power_ok, hw_error)
        VALUES (?, ?, ?)
        """, (voltage, int(fan_power_ok), int(hw_error)))

        cursor.execute("""
        DELETE FROM system_health 
        WHERE timestamp <= datetime('now', '-7 days')
        """)

        conn.commit()
    finally:
        conn.close()


def get_health():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM system_health 
    ORDER BY timestamp DESC 
    LIMIT 300
    """)

    data = cursor.fetchall()
    conn.close()
    return data

def get_config():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM config WHERE id = 1")
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

def backup_db(): #backup the database with HMAC signature 
    if not os.path.exists("backups"):
        os.makedirs("backups")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/backup_{timestamp}.db"
    sig_file = f"{backup_file}.sig"

    src_conn = get_connection()
    dst_conn = sqlite3.connect(backup_file)
    with dst_conn:
        src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()

    signature = generate_hmac(backup_file)

    with open(sig_file, "w") as f:
        f.write(signature)

    return {
        "status": "success",
        "backup": backup_file,
        "signature": sig_file
    }

def restore_db(filename): #restore the database with integrity check using HMAC signature
    backup_file = f"backups/{filename}"
    sig_file = f"{backup_file}.sig"

    if not os.path.exists(backup_file) or not os.path.exists(sig_file): 
        return {"status": "error", "message": "Backup or signature missing"}

    with open(sig_file, "r") as f: 
        original_signature = f.read() 

    current_signature = generate_hmac(backup_file) 

    if not hmac.compare_digest(original_signature, current_signature): 
        return {"status": "error", "message": "Integrity check failed!"}

    src_conn = sqlite3.connect(backup_file) 
    dst_conn = get_connection()
    with dst_conn:
        src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()
