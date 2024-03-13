from enum import Enum


class DatasetType(Enum):
    finetune_instruction_input_output = 0
    
class FinetuneEntryState(Enum):
    error = -1
    tuning = 0
    done = 1
