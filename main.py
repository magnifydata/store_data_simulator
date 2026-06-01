import threading
import time
import requests
from fastapi import FastAPI

app = FastAPI()

# 1. This gives your cloud app a basic homepage
@app.get("/")
def home():
    return {"status": "Store simulator running smoothly 24/7"}

# 2. Your actual 15-second simulation logic goes here
def run_store_simulator():
    # Insert your SUPABASE URL, KEY, and HEADERS here
    
    while True:
        try:
            # --- YOUR EXISTING LOG DATA GENERATION CODE ---
            # data = {...}
            # requests.post(f"{SUPABASE_URL}/electricity_telemetry", json=data, headers=HEADERS)
            print("Telemetry pushed to Supabase successfully.")
        except Exception as e:
            print(f"Error pushing data: {e}")
            
        time.sleep(15) # Wait 15 seconds

# 3. This starts your infinite loop in the background when the web server boots up
threading.Thread(target=run_store_simulator, daemon=True).start()