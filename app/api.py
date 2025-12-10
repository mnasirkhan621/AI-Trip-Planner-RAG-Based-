from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agent import plan_trip, load_few_shot_examples
from app.models import Itinerary

app = FastAPI(title="AI Trip Planner Agent")

class TripRequest(BaseModel):
    query: str

@app.on_event("startup")
async def startup_event():
    # Preload examples to avoid latency on first request
    print("Preloading data...")
    load_few_shot_examples()

@app.post("/plan_trip", response_model=Itinerary)
async def generate_itinerary(request: TripRequest):
    try:
        # Generate plan
        itinerary = plan_trip(request.query)
        return itinerary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Trip Planner Agent. Use POST /plan_trip to generate an itinerary."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
