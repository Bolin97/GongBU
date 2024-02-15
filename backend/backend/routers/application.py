from backend.application.scan import scan
from backend.application.llm_app import LLMApp
from fastapi import APIRouter
from backend.application.application_manager import manager

application_router = APIRouter()

@application_router.get("/")
async def get_applications():
    return list(map(lambda each: {
        "name": each.get_name(),
        "description": each.get_description(),
        "id": each.get_id()
    }, scan()))

@application_router.post("/")
async def start_application(app_id: str, deploy_id: str, name: str, description: str, port: int):
    manager.start_app(app_id, deploy_id, name, description, port)
    
@application_router.get("/running")
async def get_running_applications():
    return manager.get_running_dict()

@application_router.delete("/{pid}")
async def stop_application(pid: int):
    manager.stop(pid)
    
@application_router.put("/{pid}")
async def restart_application(pid: int):
    manager.restart(pid)
