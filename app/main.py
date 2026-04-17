# app/main.py
from fastapi import FastAPI
from .database import engine  
from .import models        
from .routes import auth     
from .routes import research

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Agent System API")

# Auth routes ko register karein
app.include_router(auth.router)
app.include_router(research.router)
@app.get("/")
def read_root():
    return {"message": "API is running successfully!"}