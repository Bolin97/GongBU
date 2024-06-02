def generate_prompt(data_point, dataset_type: int, for_infer=False):
    if dataset_type == 0:
        if "instruction" not in data_point:
            # use instruct instead
            data_point["instruction"] = data_point["instruct"]
        if "input" in data_point and len(data_point["input"]) > 0:
            return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request
### Instruction:
{data_point["instruction"]}
### Input:
{data_point["input"]}
### Response:
{data_point["output"] if not for_infer else ""}"""
        else:
            return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction:
{data_point["instruction"]}
### Response:
{data_point["output"] if not for_infer else ""}"""
    elif dataset_type == 1:
        # raw input-and-output
        if "input" in data_point and len(data_point["input"]) > 0:
            return data_point["input"] + data_point["output"] if not for_infer else data_point["input"]

        # NOT VALID