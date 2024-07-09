from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.models.schemas import ModelParams, SimulationResponse, SimulationResult
from app.services.modflow_service import ModflowService
from app.tasks.simulation_tasks import run_modflow_simulation
from app.utils.logger import setup_logger
import uuid

router = APIRouter()
logger = setup_logger(__name__)

@router.post("/run_model", response_model=SimulationResponse)
async def run_model(
    params: ModelParams,
    background_tasks: BackgroundTasks,
    modflow_service: ModflowService = Depends(ModflowService)
):
    simulation_id = str(uuid.uuid4())
    logger.info(f"Received request to run model with params: {params}, assigned simulation_id: {simulation_id}")
    run_modflow_simulation.delay(simulation_id, params.dict())
    logger.info(f"Task added to Celery queue for simulation {simulation_id}")
    return SimulationResponse(simulation_id=simulation_id, status="started")

@router.get("/simulation_status/{simulation_id}", response_model=SimulationResponse)
async def get_simulation_status(simulation_id: str, modflow_service: ModflowService = Depends(ModflowService)):
    logger.info(f"Received request for status of simulation {simulation_id}")
    status = modflow_service.get_simulation_status(simulation_id)
    if status == "not_found":
        logger.warning(f"Simulation {simulation_id} not found")
        raise HTTPException(status_code=404, detail="Simulation not found")
    logger.info(f"Returning status for simulation {simulation_id}: {status}")
    return SimulationResponse(simulation_id=simulation_id, status=status)

@router.get("/simulation_result/{simulation_id}", response_model=SimulationResult)
async def get_simulation_result(simulation_id: str, modflow_service: ModflowService = Depends(ModflowService)):
    logger.info(f"Received request for result of simulation {simulation_id}")
    result = modflow_service.get_simulation_result(simulation_id)
    if result is None:
        logger.warning(f"Result not found for simulation {simulation_id}")
        raise HTTPException(status_code=404, detail="Simulation result not found")
    logger.info(f"Returning result for simulation {simulation_id}: {result}")
    return SimulationResult(simulation_id=simulation_id, **result)