import flopy
import numpy as np
import os
import json
import redis
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class ModflowService:
    def __init__(self):
        self.model_ws = './model_files'
        self.modelname = 'simple_model'
        self.mf6_exe = 'mf6'
        self.redis = redis.Redis(host='redis', port=6379, db=0)
        logger.info(f"ModflowService initialized with model workspace: {self.model_ws}")

    def run_model(self, simulation_id: str, params: dict):
        logger.info(f"Starting model run for simulation {simulation_id}")
        try:
            # Load the existing model
            sim = flopy.mf6.MFSimulation.load(sim_ws=self.model_ws, sim_name=self.modelname, exe_name=self.mf6_exe)
            gwf = sim.get_model(self.modelname)
            logger.info(f"Model loaded successfully for simulation {simulation_id}")

            # Modify the model parameters
            npf = gwf.get_package('npf')
            npf.k.set_data(params['hk'])
            logger.info(f"Set hydraulic conductivity to {params['hk']} for simulation {simulation_id}")

            # Add or modify recharge package
            if gwf.get_package('rcha') is None:
                flopy.mf6.ModflowGwfrcha(gwf, recharge=params['recharge_rate'])
                logger.info(f"Added recharge package with rate {params['recharge_rate']} for simulation {simulation_id}")
            else:
                rch = gwf.get_package('rcha')
                rch.recharge.set_data(params['recharge_rate'])
                logger.info(f"Modified recharge rate to {params['recharge_rate']} for simulation {simulation_id}")

            # Write the updated model input files
            sim.write_simulation()
            logger.info(f"Model input files written for simulation {simulation_id}")

            # Run the model
            success, buff = sim.run_simulation()
            logger.info(f"Model run completed for simulation {simulation_id}. Success: {success}")

            if not success:
                raise Exception(f"Model run failed for simulation {simulation_id}. Buffer: {buff}")

            # Read the results
            head = gwf.output.head().get_data()
            logger.info(f"Results read for simulation {simulation_id}")

            result = {
                "max_head": float(np.max(head)),
                "min_head": float(np.min(head)),
                "mean_head": float(np.mean(head))
            }
            logger.info(f"Result calculated for simulation {simulation_id}: {result}")

            # Store the result in Redis
            self.redis.set(f"simulation:{simulation_id}:result", json.dumps(result))
            self.redis.set(f"simulation:{simulation_id}:status", "completed")
            logger.info(f"Result stored in Redis for simulation {simulation_id}")

            return result
        except Exception as e:
            logger.error(f"Error in run_model for simulation {simulation_id}: {str(e)}")
            self.redis.set(f"simulation:{simulation_id}:status", "failed")
            raise

    def get_simulation_status(self, simulation_id: str):
        logger.info(f"Fetching status for simulation {simulation_id}")
        status = self.redis.get(f"simulation:{simulation_id}:status")
        status_str = status.decode('utf-8') if status else "not_found"
        logger.info(f"Status for simulation {simulation_id}: {status_str}")
        return status_str

    def get_simulation_result(self, simulation_id: str):
        logger.info(f"Fetching result for simulation {simulation_id}")
        result = self.redis.get(f"simulation:{simulation_id}:result")
        if result:
            result_dict = json.loads(result)
            logger.info(f"Result found for simulation {simulation_id}: {result_dict}")
            return result_dict
        else:
            logger.warning(f"No result found for simulation {simulation_id}")
            return None