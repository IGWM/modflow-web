from fastapi import FastAPI
from app.routers import simulation
from app.celery_app import celery_app  # Add this line

app = FastAPI()

app.include_router(simulation.router, prefix="/api/v1", tags=["simulation"])


app = FastAPI(
    title="MODFLOW Web API",
    description="A web API for running MODFLOW simulations",
    version="1.0.0",
)

app.include_router(simulation.router, prefix="/api/v1", tags=["simulation"])

@app.get("/")
async def root():
    return {"message": "Welcome to the MODFLOW Web API"}