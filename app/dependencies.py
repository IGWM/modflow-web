from app.services.modflow_service import ModflowService

def get_modflow_service():
    return ModflowService(mf6_exe='mf6')