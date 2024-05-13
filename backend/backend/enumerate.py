from enum import Enum


class DatasetType(Enum):
    finetune_instruction_input_output = 0


class FinetuneState(Enum):

    error = -1
    running = 0
    done = 1


class DeploymentState(Enum):

    error = -1
    stopped = 0
    starting = 1
    running = 2


class FaultCode(Enum):

    cuda_oom = 10000

    other = 99999
    
    nccl_issue = 199999


class TaskType(Enum):

    finetune = "ft"
    evaluation = "eval"
    deployment = "depl"


class EvalState(Enum):

    error = -1
    loading_model = 0
    starting = 1
    generating = 2
    evaluating = 3
    done = 4
