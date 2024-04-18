from enum import Enum


class DatasetType(Enum):
    finetune_instruction_input_output = 0


class FinetuneEntryState(Enum):

    other_error = -1
    tuning = 0
    done = 1


class DeploymentState(Enum):

    other_error = -1
    stopped = 0
    starting = 1
    running = 2


class Fault(Enum):

    cuda_oom = 10000

    rtx_4000_not_implemented = 10001

    unkown_runtime_error = 99999


class FaultSource(Enum):

    finetune = "ft"
    evaluation = "eval"


class EvalState(Enum):

    other_error = -1
    loading_model = 0
    starting = 1
    generating = 2
    evaluating = 3
    done = 4
