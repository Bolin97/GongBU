def get_reference_output(data_point, ds_type):
    if ds_type == 0 or ds_type == 1:
        return data_point.get("output", "")
    elif ds_type == 2:
        text = data_point.get('text', '')
        if isinstance(text, str):
            sentences = text.split('\n')
        else:
            sentences = text
        return sentences[-1] if len(sentences) >= 1 else ""
    elif ds_type == 3:
        return data_point.get("category", "")
    elif ds_type == 4:
        translation = data_point.get('translation', {})
        keys = list(translation.keys())
        return translation[keys[1]] if len(keys) > 1 else ""
    elif ds_type == 5:
        return data_point.get('highlights', '')
    elif ds_type == 6:
        return data_point.get('answers', '').get("text", "")[0]
    elif ds_type == 7:
        return data_point.get('label', '')
    else:
        return ""


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
        keys = data_point.keys()
        return "".join([data_point[k] for k in keys])
    elif dataset_type == 2:
        text = data_point['text']
        if isinstance(text, str):
            sentences = text.split('\n')
        else:
            sentences = text
        input_part = '\n'.join(sentences[:-1]) if len(sentences) > 1 else (sentences[0] if sentences else "")
        output_part = sentences[-1] if len(sentences) >= 1 else ""
        return f"""Below is an input that provides context. Write a response that continues the text.
### Input:
{input_part}
### Response:
{output_part if not for_infer else ''}"""
    elif dataset_type == 3:
        instruction = data_point.get("instruction", "")
        context = data_point.get("context", "")
        category = data_point.get("category", "")
        if context.strip():
            return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.
### Instruction:
{instruction}
### Input:
{context}
### Response:
{category if not for_infer else ''}"""
        else:
            return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction:
{instruction}
### Response:
{category if not for_infer else ''}"""
    elif dataset_type == 4:
        translation = data_point['translation']
        keys = list(translation.keys())
        input_text = translation[keys[0]] if len(keys) > 0 else ""
        output_text = translation[keys[1]] if len(keys) > 1 else ""
        return f"""Below is a translation task. Translate the input into the target language.
### Input:
{input_text}
### Response:
{output_text if not for_infer else ''}"""
    elif dataset_type == 5:
        article = data_point.get('article', '')
        highlights = data_point.get('highlights', '')
        return f"""Below is an article. Write a summary that highlights the key points.
### Input:
{article}
### Response:
{highlights if not for_infer else ''}"""
    elif dataset_type == 6:
        question = data_point.get('question', '')
        context = data_point.get('context', '')
        answers = data_point.get('answers', '').get('text')[0]
        if context.strip():
            return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.
### Instruction:
{question}
### Input:
{context}
### Response:
{answers if not for_infer else ''}"""
        else:
            return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction:
{question}
### Response:
{answers if not for_infer else ''}"""
    elif dataset_type == 7:
        text = data_point.get("text", "")
        label = data_point.get("label", "")
        return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Input:
{text}
### Response:
{label if not for_infer else ''}"""
    else:
        raise ValueError(f"Unsupported dataset type: {dataset_type}")
