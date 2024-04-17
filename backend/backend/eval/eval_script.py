import datetime
from backend.eval.evaluate import evaluate
from backend.service.dataset import fetch_dataset, submit_evaluation_data, submit_evaluation_generation
from backend.tuner.generate_prompt import generate_prompt
from fire import Fire
from backend.llmw import LLMW
from backend.db import get_db
from backend.models import *
from pandas import DataFrame
import datasets
from tqdm import tqdm

def get_dataset(dataset_id: int, val_size: float, entry_id: int) -> tuple[list, int]:
    dataset_json_obj, dataset_type = fetch_dataset(dataset_id)
    df = DataFrame(dataset_json_obj)
    data = datasets.DatasetDict(
        {"train": datasets.Dataset.from_dict(df.to_dict("list"))}
    )
    val_size = max(int(val_size * len(data["train"])), 2)
    if val_size == len(data["train"]):
        return data["train"], dataset_type
    else:
        train_val = data["train"].train_test_split(
            test_size=val_size, shuffle=True, seed=42
        )
        submit_evaluation_data(entry_id, train_val["test"])
        return train_val["test"], dataset_type
    
def progress_increment(entry_id: int, total: int):
    db = get_db()
    entry = db.query(EvaluationProgress).filter(EvaluationProgress.entry_id == entry_id).first()
    entry.current += 1
    entry.total = total
    db.commit()
    db.close()

def run(
    evaluation_id: int
):
    db = get_db()
    
    entry = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    model_or_adapter_id = entry.model_or_adapter_id
    deploy_base_model = entry.deploy_base_model
    bits_and_bytes = entry.bits_and_bytes
    load_8bit = entry.load_8bit
    load_4bit = entry.load_4bit
    use_flash_attention = entry.use_flash_attention
    use_deepspeed = entry.use_deepspeed
    devices = entry.devices
    indexes = entry.indexes
    
    llmw = None
    if deploy_base_model:
        model = db.query(OpenLLM).filter(OpenLLM.id == model_or_adapter_id).first()
        llmw = LLMW(model.local_path, None)
    else:
        adapter = db.query(Adapter).filter(Adapter.id == model_or_adapter_id).first()
        base_model = db.query(OpenLLM).filter(OpenLLM.model_name == adapter.base_model_name).first()
        llmw = LLMW(base_model.local_path, adapter.local_path)
    llmw.load()
    entry.state = 1
    db.commit()
    
    eval_dataset, ds_type = get_dataset(entry.dataset_id, entry.val_set_size, entry.id)
    
    def get_generated_output(data_point):
        prompt = generate_prompt(data_point, ds_type, for_infer=True)
        return llmw.simple_text_generation(prompt, len(generate_prompt(data_point, ds_type, for_infer=False)))

    cands = []
    for each in tqdm(eval_dataset):
        res = get_generated_output(each)
        cands.append(res)  
        each["generated_output"] = res
        progress_increment(entry.id, len(eval_dataset))
    refs = list(map(lambda data_point: data_point["output"], eval_dataset))
    submit_evaluation_generation(entry.id, eval_dataset)
    entry.state = 2
    db.commit()
    
    eval_result = evaluate(indexes, refs, cands)
    entry.state = 3
    entry.result = eval_result
    entry.end_time = datetime.datetime.utcnow()
    db.commit()
    db.close()
    
if __name__ == "__main__":
    Fire(run)