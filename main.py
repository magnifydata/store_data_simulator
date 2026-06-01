import threading
import time
import random
import requests
from fastapi import FastAPI

app = FastAPI()

SUPABASE_URL = "https://knuwshedoxgapnfogjju.supabase.co/rest/v1"
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

@app.get("/")
def home():
    return {"status": "Enterprise supermarket data pipeline active 24/7"}

def run_store_simulator():
    print("Background telemetry engine initiated.")
    while True:
        try:
            # 1. GENERATE & PUSH ENVIRONMENT FLOOR PLAN DATA
            for section in FLOOR_SECTIONS:
                # Assign realistic baselines depending on the store area
                if 'Chiller' in section:
                    temp = random.uniform(1.5, 4.5)
                    hum = random.uniform(50, 60)
                elif 'Cold cuts' in section:
                    temp = random.uniform(4.0, 7.5)
                    hum = random.uniform(40, 50)
                elif 'Kitchen' in section:
                    temp = random.uniform(28.0, 32.5)
                    hum = random.uniform(50, 65)
                elif 'Bakery' in section:
                    temp = random.uniform(26.0, 30.0)
                    hum = random.uniform(45, 55)
                else:
                    temp = random.uniform(21.0, 26.0)
                    hum = random.uniform(40, 50)

                sensor_payload = {
                    "section_name": section,
                    "temperature": temp,
                    "humidity": hum,
                    "co2": int(random.uniform(400, 800))
                }
                requests.post(f"{SUPABASE_URL}/sensor_telemetry", json=sensor_payload, headers=HEADERS)

            # 2. GENERATE & PUSH LIVE ELECTRICITY METRICS
            elec_payload = {
                "usage_store": random.uniform(100, 150),
                "usage_chillers": random.uniform(580, 620),
                "usage_ac": random.uniform(380, 500),
                "usage_lighting": random.uniform(75, 90),
                "usage_bakery": random.uniform(140, 190),
                "usage_outdoor": random.uniform(45, 55),
                "generated_solar": random.uniform(750, 950) if 7 <= time.localtime().tm_hour <= 18 else 0.0
            }
            requests.post(f"{SUPABASE_URL}/electricity_telemetry", json=elec_payload, headers=HEADERS)

            # 3. GENERATE & PUSH LIVE POS QUEUES
            for lane in range(1, 11):
                pos_payload = {
                    "lane_number": lane,
                    "is_open": True if lane <= 6 else random.choice([True, False]),
                    "queue_length": int(random.uniform(0, 5)) if lane <= 6 else (int(random.uniform(0, 2)) if random.choice([True, False]) else 0)
                }
                requests.post(f"{SUPABASE_URL}/pos_telemetry", json=pos_payload, headers=HEADERS)

            # 4. GENERATE & PUSH FOOTFALL STREAM
            footfall_payload = {
                "people_count": int(random.uniform(5, 25)) if 10 <= time.localtime().tm_hour <= 21 else 0
            }
            requests.post(f"{SUPABASE_URL}/footfall_telemetry", json=footfall_payload, headers=HEADERS)

            # 5. GENERATE & PUSH DEMOGRAPHICS TRANSACTION LOGS
            if 10 <= time.localtime().tm_hour <= 21:
                demo_payload = {
                    "gender": random.choice(["Female", "Male"]),
                    "age_group": random.choice(['Children (< 12)', 'Teenagers (13 - 25)', 'Older Teenagers (26 - 30)', 'Adults (31 - 50)', 'Older Adults (51 - 60)', 'Elderly (> 60)'])
                }
                requests.post(f"{SUPABASE_URL}/demographics_log", json=demo_payload, headers=HEADERS)

            print("Complete telemetric matrix successfully broadcasted to Supabase.")
            
        except Exception as e:
            print(f"Data broadcast exception encountered: {e}")
            
        time.sleep(15)

# Initialize simulation within a dedicated daemon thread
threading.Thread(target=run_store_simulator, daemon=True).start()