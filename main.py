import threading
import time
import random
import requests
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI

# 1. Initialize FastAPI so Render can bind to it successfully
app = FastAPI()

@app.get("/")
def home():
    return {"status": "Supermarket AI & IoT Cloud Simulator is running 24/7"}

# --- Supabase Configuration ---
SUPABASE_URL = "https://knuwshedoxgapnfogjju.supabase.co"
SUPABASE_KEY = "sb_publishable_3CwfUy1a2qhyZwrWlCMn-w_kQkuMl-r"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

FLOOR_SECTIONS = [
    'Entrance Area', 'POS area', 'Aisle 1', 'Aisle 2',
    'Aisle 3', 'Chiller area', 'Bakery area', 'Cold cuts',
    'Kitchen', 'Auxiliary Area'
]

AGE_GROUPS = [
    'Children (< 12)', 'Teenagers (13 - 25)', 'Older Teenagers (26 - 30)',
    'Adults (31 - 50)', 'Older Adults (51 - 60)', 'Elderly (> 60)'
]
GENDERS = ['Male', 'Female']

def post_data(table_name, payload):
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code not in [201, 204]:
            print(f"❌ Error posting to {table_name}: {response.text}")
    except Exception as e:
        print(f"❌ Connection error on {table_name}: {e}")

# 2. Your core telemetric simulation engine runs inside a background worker thread
def run_store_simulator():
    print("🚀 Starting Supermarket AI & IoT Cloud Simulator Background Thread...")
    while True:
        try:
            now_utc = datetime.now(timezone.utc)
            now_myt = now_utc + timedelta(hours=8)
            current_time_str = now_myt.strftime("%Y-%m-%d %H:%M:%S")
            current_hour = now_myt.hour

            # Determine if the store is actively open (10:00 AM to 9:59 PM)
            is_store_open = 10 <= current_hour < 22

            print(f"--- Generating Cloud Telemetry at {current_time_str} (MYT) ---")

            # A. Temperature & Environment Telemetry (Runs 24/7)
            for idx, section in enumerate(FLOOR_SECTIONS):
                base_temp = 4 if "Chiller" in section or "Cold" in section else 24
                if "Kitchen" in section or "Bakery" in section:
                    base_temp = 30

                temp = base_temp + random.uniform(-2, 5)

                # 2% chance to trigger an anomaly event
                if random.random() < 0.02:
                    temp = random.uniform(41, 45)

                env_payload = {
                    "sensor_id": f"SENS-{idx + 1:02d}",
                    "section_name": section,
                    "temperature": round(temp, 1),
                    "humidity": random.randint(40, 65),
                    "co2": random.randint(400, 800)
                }
                post_data("sensor_telemetry", env_payload)

            # B. POS Queue Data (Queues automatically flush to 0 if closed)
            num_open_lanes = random.randint(3, 7) if is_store_open else 0
            pos_payload_batch = []
            for lane in range(1, 11):
                is_open = lane <= num_open_lanes
                queue = random.randint(1, 8) if is_open else 0
                pos_payload_batch.append({
                    "lane_number": lane,
                    "is_open": is_open,
                    "queue_length": queue
                })
            post_data("pos_telemetry", pos_payload_batch)

            # C. Footfall and Customer Demographics (Only active during store hours)
            if is_store_open:
                people_entering = random.randint(2, 12)
                footfall_payload = {
                    "entrance_name": "Main Entrance",
                    "people_count": people_entering
                }
                post_data("footfall_telemetry", footfall_payload)

                demographics_batch = []
                for _ in range(people_entering):
                    demographics_batch.append({
                        "gender": random.choices(GENDERS, weights=[45, 55])[0],
                        "age_group": random.choices(AGE_GROUPS, weights=[10, 20, 10, 40, 15, 5])[0]
                    })
                post_data("demographics_log", demographics_batch)
            else:
                print("🌙 Store Closed. Skipping Footfall & Demographics logging.")

            # D. Electricity Telemetry (kW)
            solar_gen = 0
            if 6 <= current_hour <= 19:
                if current_hour < 9:
                    solar_gen = random.uniform(10, 30)
                elif current_hour < 15:
                    solar_gen = random.uniform(60, 95)
                else:
                    solar_gen = random.uniform(20, 50)

            elec_payload = {
                "usage_chillers": round(random.uniform(25, 30), 1),
                "usage_outdoor": round(random.uniform(3, 5), 1),
                "usage_ac": round(random.uniform(40, 55) if is_store_open else random.uniform(5, 10), 1),
                "usage_lighting": round(random.uniform(12, 15) if is_store_open else random.uniform(2, 4), 1),
                "usage_bakery": round(random.uniform(15, 25) if is_store_open else random.uniform(0, 1), 1),
                "usage_store": round(random.uniform(5, 10) if is_store_open else random.uniform(1, 3), 1),
                "generated_solar": round(solar_gen, 1)
            }
            post_data("electricity_telemetry", elec_payload)
            print("✅ Telemetric data broadcasted to Supabase successfully.")

        except Exception as e:
            print(f"❌ Error in background simulation sequence: {e}")
            
        time.sleep(15)

# 3. Spin up the background looping thread safely
threading.Thread(target=run_store_simulator, daemon=True).start()