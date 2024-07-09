from pydantic import BaseModel

class ModelParams(BaseModel):
    hk: float
    recharge_rate: float

class SimulationResponse(BaseModel):
    simulation_id: str
    status: str

class SimulationResult(BaseModel):
    simulation_id: str
    max_head: float
    min_head: float
    mean_head: float