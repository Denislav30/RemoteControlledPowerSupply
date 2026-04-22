import asyncio
import subprocess
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.responses import FileResponse

# Import DPL for database logging
sys.path.insert(0, str(Path(__file__).parent.parent / "database"))
try:
    import DPL
except ImportError:
    DPL = None

# --- Security Config ---
SECRET_KEY = "olimex_secret_key_change_this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- System State ---
class SystemState:
    def __init__(self):
        self.manual_mode = False
        self.thresholds = [28.0, 30.0, 32.0]
        self.hysteresis = 0.5
        self.current_temp = 0.0
        self.voltage = 0.0
        self.fan_power_ok = True
        self.hw_error = False
        self.fans = [False, False, False]

state = SystemState()

# --- Security Functions ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != "admin":
            raise HTTPException(status_code=401)
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# --- Hardware Sync ---
def update_hw():
    led = "1" if state.manual_mode else "0"
    f_vals = ["1" if f else "0" for f in state.fans]
    try:
        # subprocess.check_output([sys.executable, "../hardware/dummy/DOUT_write.py", led, *f_vals], timeout=1)
        subprocess.check_output([sys.executable, "../hardware/real/DOUT_write.py", led, *f_vals], timeout=1)
        state.hw_error = False
    except:
        state.hw_error = True

async def control_loop():
    while True:
        try:
            # raw = subprocess.check_output([sys.executable, "../hardware/dummy/ADC_read.py"], text=True, timeout=1).strip()
            raw = subprocess.check_output([sys.executable, "../hardware/real/ADC_read.py"], text=True, timeout=1).strip()
            state.hw_error = False
            t, v = map(float, raw.split(','))
            state.current_temp, state.voltage = t, v * 4.3
            state.fan_power_ok = (v * 4.3) > 10.0
            if not state.manual_mode:
                for i in range(3):
                    if not state.fans[i] and t >= state.thresholds[i]: state.fans[i] = True
                    elif state.fans[i] and t <= (state.thresholds[i] - state.hysteresis): state.fans[i] = False
                update_hw()
            
            # Log data to database
            if DPL:
                reason = "manual" if state.manual_mode else "auto"
                DPL.insert_log(state.current_temp, state.fans, reason)
                DPL.insert_health(state.voltage, int(state.fan_power_ok), int(state.hw_error))
        except:
            state.hw_error = True
            state.fans = [True, True, True]
        await asyncio.sleep(2)

@app.on_event("startup")
async def startup():
    if DPL:
        DPL.init_db()
    asyncio.create_task(control_loop())

# --- Auth Endpoint ---
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "admin" and form_data.password == "admin":
        access_token = create_access_token(data={"sub": "admin"})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

# --- Protected API Endpoints ---
@app.get("/status")
def get_status():
    return {
        "system_mode": "MANUAL" if state.manual_mode else "AUTO",
        "sensor_data": {"temperature": state.current_temp, "power_supply": f"{state.voltage:.1f}V", "power_alert": (any(state.fans) and not state.fan_power_ok), "hw_error": state.hw_error},
        "fans": state.fans,
        "config": {"thresholds": state.thresholds}
    }

@app.post("/mode")
def set_mode(manual: bool, user: str = Depends(verify_token)):
    state.manual_mode = manual
    update_hw()

@app.post("/fans/{fan_id}")
def manual_fan(fan_id: int, on: bool, user: str = Depends(verify_token)):
    if not state.manual_mode: raise HTTPException(status_code=403)
    if 1 <= fan_id <= 3:
        state.fans[fan_id-1] = on
        update_hw()

@app.post("/thresholds")
def set_thresholds(t: List[float], user: str = Depends(verify_token)):
    if len(t) == 3:
        state.thresholds = sorted(t)
        return {"status": "ok"}
    raise HTTPException(status_code=400)

@app.get("/api/history")
def get_history():
    if not DPL:
        raise HTTPException(status_code=500, detail="Database layer is not available")

    return {"data": DPL.get_logs()}


@app.get("/api/health")
def get_health():
    if not DPL:
        raise HTTPException(status_code=500, detail="Database layer is not available")

    return {"data": DPL.get_health()}


@app.get("/api/config")
def get_config():
    if not DPL:
        raise HTTPException(status_code=500, detail="Database layer is not available")

    return {"data": DPL.get_config()}

FRONTEND_DIR = Path(__file__).parent / "frontend"

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    requested_path = FRONTEND_DIR / full_path

    if full_path and requested_path.exists() and requested_path.is_file():
        return FileResponse(requested_path)

    return FileResponse(FRONTEND_DIR / "index.html")