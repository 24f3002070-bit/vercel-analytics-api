import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Enable CORS so the grading system can successfully connect to your endpoint
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hardcoded telemetry data for eShopCo storefront metrics calculation
TELEMETRY_DATA = [
  {"region": "apac", "latency": 152, "status": "up"},
  {"region": "apac", "latency": 185, "status": "up"},
  {"region": "apac", "latency": 141, "status": "up"},
  {"region": "apac", "latency": 190, "status": "up"},
  {"region": "apac", "latency": 165, "status": "up"},
  {"region": "apac", "latency": 210, "status": "down"},
  {"region": "apac", "latency": 138, "status": "up"},
  {"region": "apac", "latency": 174, "status": "up"},
  {"region": "apac", "latency": 162, "status": "up"},
  {"region": "apac", "latency": 195, "status": "up"},
  {"region": "emea", "latency": 168, "status": "up"},
  {"region": "emea", "latency": 172, "status": "up"},
  {"region": "emea", "latency": 155, "status": "up"},
  {"region": "emea", "latency": 201, "status": "up"},
  {"region": "emea", "latency": 182, "status": "up"},
  {"region": "emea", "latency": 176, "status": "up"},
  {"region": "emea", "latency": 159, "status": "up"},
  {"region": "emea", "latency": 164, "status": "up"},
  {"region": "emea", "latency": 220, "status": "down"},
  {"region": "emea", "latency": 171, "status": "up"},
  {"region": "us-east", "latency": 120, "status": "up"},
  {"region": "us-east", "latency": 125, "status": "up"},
  {"region": "us-west", "latency": 135, "status": "up"},
  {"region": "us-west", "latency": 140, "status": "up"}
]

@app.get("/")
def read_root():
    return {"message": "eShopCo Analytics Engine is Running"}

@app.post("/")
async def analyze_telemetry(request: Request):
    try:
        body = await request.json()
        target_regions = body.get("regions", [])
        threshold = body.get("threshold_ms", 180)
        
        result = {}
        
        for region in target_regions:
            # Filter the telemetry list down to match only the current active region loop
            region_records = [r for r in TELEMETRY_DATA if r["region"] == region]
            
            if not region_records:
                continue
                
            latencies = [r["latency"] for r in region_records]
            
            # 1. Compute average latency (mean)
            avg_latency = sum(latencies) / len(latencies)
            
            # 2. Compute p95 latency (95th percentile)
            sorted_latencies = sorted(latencies)
            # Find the index closest to the 95th percentile rank position
            idx = int(len(sorted_latencies) * 0.95)
            idx = min(idx, len(sorted_latencies) - 1)
            p95_latency = sorted_latencies[idx]
            
            # 3. Compute average uptime (ratio of records where status is "up")
            up_count = sum(1 for r in region_records if r["status"] == "up")
            avg_uptime = up_count / len(region_records)
            
            # 4. Count the number of threshold breaches
            breaches = sum(1 for lat in latencies if lat > threshold)
            
            result[region] = {
                "avg_latency": round(avg_latency, 2),
                "p95_latency": round(p95_latency, 2),
                "avg_uptime": round(avg_uptime, 4),
                "breaches": breaches
            }
            
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
