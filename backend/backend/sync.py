import torch

ctx = torch.multiprocessing.get_context("spawn")

class SafeDict(dict):
    lock: any
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = ctx.Lock()

    def __setitem__(self, key, value):
        with self.lock:
            super().__setitem__(key, value)

    def __getitem__(self, key):
        with self.lock:
            return super().__getitem__(key)

    def __delitem__(self, key):
        with self.lock:
            super().__delitem__(key)

    def __contains__(self, key):
        with self.lock:
            return super().__contains__(key)

    def __len__(self):
        with self.lock:
            return super().__len__()
    
    def __iter__(self):
        with self.lock:
            return super().__iter__()
    
    def __repr__(self):
        with self.lock:
            return super().__repr__()
    
    def __str__(self):
        with self.lock:
            return super().__str__()
    
    def __hash__(self):
        with self.lock:
            return super().__hash__()