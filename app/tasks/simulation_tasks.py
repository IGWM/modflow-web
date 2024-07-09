from app.celery_app import celery_app
from app.services.modflow_service import ModflowService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

@celery_app.task(name="run_modflow_simulation")
def run_modflow_simulation(simulation_id: str, params: dict):
    logger.info(f"Starting simulation {simulation_id} with params: {params}")
    service = ModflowService()
    try:
        result = service.run_model(simulation_id, params)
        logger.info(f"Simulation {simulation_id} completed successfully. Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Simulation {simulation_id} failed with error: {str(e)}")
        raise