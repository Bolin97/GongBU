from enum import Enum


class DatasetType(Enum):
    finetune_instruction_input_output = 0
    
class FinetuneEntryState(Enum):
    
    other_error = -1
    tuning = 0
    done = 1

class Fault(Enum):

    finetune_cuda_oom = 1000

    finetune_unkown_runtime_error = 1999

    eval_cuda_oom = 2000
    
    eval_unknown_runtime_error = 2999
    
class FaultSource(Enum):
    
    finetune = "ft"
    evaluation = "eval"