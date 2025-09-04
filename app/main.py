from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()
env = os.getenv("APP_ENV")
debug = os.getenv("APP_DEBUG")

app = FastAPI(
    title="Retail Insights API",
    description="Initial Hello World API for development environment check",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Hello, Retail Insights API is running!"}
