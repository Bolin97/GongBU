from backend.sync import SafeDict
import os
import signal

from psutil import NoSuchProcess
from .scan import scan
from backend.deployment.deployment_manager import manager as deployment_manager
from .llm_app import LLMApp
from backend.sync import ctx
   
def terminate_proc(pid: int):
    os.kill(pid, signal.SIGKILL)

class ApplicationInstanceEntry:
    
    name: str
    description: str
    app_name: str
    deploy_id: str
    info: str
    def __init__(self, name: str, description: str, app_name: str, deploy_id: str, info: str):
        self.name = name
        self.description = description
        self.app_name = app_name
        self.deploy_id = deploy_id
        self.info = info
    
class ApplicationManager:

    running: SafeDict[int, ApplicationInstanceEntry]
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ApplicationManager, cls).__new__(cls)
        if cls.instance is not None:
            print("ApplicationManager is a singleton class, it will return the same instance every time.")
            return cls.instance
        return cls.instance
    
    def __init__(self):
        self.running = SafeDict()
        
    def get_running_dict(self):
        return list(map(lambda each: {
                "pid": each[0],
                "name": each[1].name,
                "description": each[1].description,
                "app_name": each[1].app_name,
                "deploy_id": each[1].deploy_id,
                "info": each[1].info
            }, self.running.items())
        )
     
    def start_app(self, app_id: str, deploy_id: int, name: str, description: str, port: int):
        scan_result = scan()
        app_cls  = None
        for each in scan_result:
            if each.get_id() == app_id:
                app_cls = each
                break
        if app_cls is None:
            return
        app = app_cls(deployment_manager.deployments[deploy_id], port)
        app_entry = ApplicationInstanceEntry(name, description, app.get_name(), deploy_id, app.get_startup_info())
        proc = ctx.Process(target=app.run)
        proc.start()
        self.running[proc.pid] = app_entry
  
    def restart(self, pid: int):
        if pid in self.running:
            self.stop(pid)
            app_entry = self.running[pid]
            self.start_app(app_entry.app_name, app_entry.injected_url, app_entry.name, app_entry.description)

    def stop(self, pid: int):
        if pid in self.running:
            try:
                terminate_proc(pid)
                self.running.pop(pid)
            except NoSuchProcess:
                self.running.pop(pid)
    
manager = ApplicationManager()