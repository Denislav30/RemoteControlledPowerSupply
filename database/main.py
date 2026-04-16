from fastapi import FastAPI
import DPL

app = FastAPI()

DPL.init_db()

@app.get("/")
def home():
    return {"message": "API works"}

@app.get("/api/history")
def get_history():
    return {"data": DPL.get_logs()}

@app.post("/api/log")
def add_log(temp: float, fan1: int, fan2: int, fan3: int, reason: str):
    fans = [fan1, fan2, fan3]
    DPL.insert_log(temp, fans, reason)
    return {"status": "log added"}

@app.post("/api/health")
def add_health(voltage: float, fan_power_ok: int, hw_error: int):
    DPL.insert_health(voltage, fan_power_ok, hw_error)
    return {"status": "health record added"}

@app.get("/api/health")
def get_health():
    return {"data": DPL.get_health()}

@app.get("/api/config")
def get_config():
    return {"data": DPL.get_config()}

@app.post("/api/config")
def update_config(t1: float, t2: float, t3: float, hysteresis: float, mode: str):
    DPL.update_config(t1, t2, t3, hysteresis, mode)
    return {"status": "config updated"}

#RESTORE & BACKUP TBD
