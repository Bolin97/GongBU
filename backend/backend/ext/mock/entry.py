from backend.deployment.deployment_manager import LLMWrapper

class Main:
    
    def __init__(self, llm: LLMWrapper, port: int):
        self.llm = llm
        self.port = port
    
    def get_startup_info(self) -> str:
        return f"{self.port} is the port"
    
    @staticmethod
    def get_name(cls) -> str:
        return "Mocking App"
    @staticmethod
    def get_description(cls) -> str:
        return "Mocking App Description"
    @staticmethod
    def get_id(self) -> str:
        return "Mocking"

    def run(self):
        with open("mocking.txt", "w") as f:
            f.write("Mocking")