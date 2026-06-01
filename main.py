import threading
import time
import random
import requests
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Enterprise supermarket data pipeline active 24/7"}

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

def run_store_simulator():
    print("🚀 Starting Supermarket AI & IoT Cloud Simulator Background Thread...")
    while True:
        try:
            now_utc = datetime.now(timezone.utc)
            now_myt = now_utc + timedelta(hours=8)
            current_time_str = now_myt.strftime("%Y-%m-%d %H:%M:%S")
            current_hour = now_myt.hour
            current_minute = now_myt.minute
            
            # Convert time to a precise decimal float for flawless transitional stepping
            time_float = current_hour + (current_minute / 60.0)

            # Store operational window: 10:00 AM to 10:00 PM
            is_store_open = 10.0 <= time_float < 22.0

            print(f"--- Generating Cloud Telemetry at {current_time_str} (MYT) ---")

            # 1. Temperature & Environment Telemetry (Runs 24/7)
            for idx, section in enumerate(FLOOR_SECTIONS):
                base_temp = 4 if "Chiller" in section or "Cold" in section else 24
                if "Kitchen" in section or "Bakery" in section:
                    base_temp = 30

                temp = base_temp + random.uniform(-2, 5)

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

            # 2. POS Queue Data 
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

            # 3 & 4. Footfall and Customer Demographics
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

            # 5. NEW METRIC ENGINE: High-Accuracy Grid Usage Profile (kW)
            usage_chillers = 0.0
            usage_outdoor = 0.0
            usage_ac = 0.0
            usage_lighting = 0.0
            usage_bakery = 0.0
            usage_store = 0.0

            # MODE A: Night Closure Window (00:00 to 07:30) -> Sums tightly to ~5.3kW - 6.3kW
            if 0.0 <= time_float < 7.5:
                usage_chillers = random.uniform(4.0, 4.4)
                usage_outdoor = random.uniform(1.0, 1.3)
                usage_ac = random.uniform(0.1, 0.2)
                usage_lighting = random.uniform(0.1, 0.2)
                usage_bakery = 0.0
                usage_store = random.uniform(0.1, 0.2)

            # MODE B: Morning Pre-Open Window (07:30 to 10:00) -> Drops further to ~4.3kW - 5.1kW (Outdoor Off)
            elif 7.5 <= time_float < 10.0:
                usage_chillers = random.uniform(4.0, 4.4)
                usage_outdoor = 0.0 
                usage_ac = random.uniform(0.1, 0.2)
                usage_lighting = random.uniform(0.1, 0.2)
                usage_bakery = random.uniform(0.0, 0.1)
                usage_store = random.uniform(0.1, 0.2)

            # MODE C: Active Store Hours (10:00 to 22:00) -> Sums securely to your target ~15kW - 25kW
            elif 10.0 <= time_float < 22.0:
                usage_chillers = random.uniform(6.5, 8.5)
                usage_outdoor = 0.0
                usage_ac = random.uniform(5.5, 8.5)
                usage_lighting = random.uniform(2.0, 3.5)
                usage_bakery = random.uniform(1.5, 3.0)
                usage_store = random.uniform(1.0, 2.0)

            # MODE D: Late Night Transition (22:00 to 24:00) -> Mimics night baseline, security lighting on
            else:
                usage_chillers = random.uniform(4.0, 4.4)
                usage_outdoor = random.uniform(1.0, 1.3)
                usage_ac = random.uniform(0.1, 0.2)
                usage_lighting = random.uniform(0.1, 0.2)
                usage_bakery = 0.0
                usage_store = random.uniform(0.1, 0.2)

            # Solar Array Day Curve (6 AM to 7 PM)
            solar_gen = 0.0
            if 6.0 <= time_float <= 19.0:
                if time_float < 9.0:
                    solar_gen = random.uniform(10.0, 30.0)
                elif time_float < 15.0:
                    solar_gen = random.uniform(60.0, 95.0)
                else:
                    solar_gen = random.uniform(20.0, 50.0)

            elec_payload = {
                "usage_chillers": round(usage_chillers, 1),
                "usage_outdoor": round(usage_outdoor, 1),
                "usage_ac": round(usage_ac, 1),
                "usage_lighting": round(usage_lighting, 1),
                "usage_bakery": round(usage_bakery, 1),
                "usage_store": round(usage_store, 1),
                "generated_solar": round(solar_gen, 1)
            }
            
            post_data("electricity_telemetry", elec_payload)
            print("✅ Precision power metrics synchronized with Supabase.")

        except Exception as e:
            print(f"❌ Error in background simulation sequence: {e}")
            
        time.sleep(15)

threading.Thread(target=run_store_simulator, daemon=True).start()