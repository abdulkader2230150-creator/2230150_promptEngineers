from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.get("/api/state")
async def get_state():
    try:
        with open("state.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {} # Dashboard stays empty until the first message arrives