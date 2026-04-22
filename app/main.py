import logging
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI lab working "}

@app.get("/health")
def health():
    return {"status": "Ok"}
