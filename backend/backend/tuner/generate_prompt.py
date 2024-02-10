def generate_prompt(data_point, for_infer=False):
    # sorry about the formatting disaster gotta move fast
    if "input" in data_point and len(data_point["input"]) > 0:
        return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request
### Instruction:
{data_point["instruction"]}     
### Input:
{data_point["input"]}
### Response:
{data_point["output"] if not for_infer else ""}"""  # noqa: E501
    else:
        return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction:
{data_point["instruction"]}
### Response:
{data_point["output"] if not for_infer else ""}"""  # noqa: E501
