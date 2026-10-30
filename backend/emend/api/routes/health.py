import os
from fastapi import APIRouter
from ...core.agent.router import ModelRouter
from ...core.nebius_client import NebiusClient

router = APIRouter(prefix="/api/health", tags=["health"])
model_router = ModelRouter()

@router.get("")
async def health_check():
    client = NebiusClient()
    model_info = model_router.describe()
    
    return {
        "status": "healthy",
        "service": "Emend Autonomous Code-Repair API",
        "mode": os.environ.get("RUN_MODE", "hosted"),
        "models": {
            "repair_model": model_info["repair_model"],
            "fast_model": model_info["fast_model"],
            "provider": model_info["provider"],
            "live_tokenfactory_active": client.is_live,
            "offline_simulation_ready": True
        },
        "version": "1.0.0"
    }
