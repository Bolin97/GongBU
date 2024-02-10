

class Main:
    
    gr_url: str
    port: int
    
    def __init__(self, gr_url: str, port: int):
        self.gr_url = gr_url
        self.port = port
    
    def get_front_page_url(self) -> str:
        return "http://www.baidu.com"
    @staticmethod
    def get_id() -> str:
        return "Mock"
    
    @staticmethod
    def get_name() -> str:
        return "Mock"
    
    @staticmethod
    def get_description() -> str:
        return "Mock app for testing purposes."
    
    def run(self):
        with open("/data/yimin/project/a.txt", "w") as f:
            f.write(f"{self.gr_url} {self.port}")
            
