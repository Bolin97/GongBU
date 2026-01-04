import threading
import requests
from transformers import TrainerCallback
from transformers.generation.stopping_criteria import StoppingCriteriaList
from transformers.trainer_callback import TrainerControl, TrainerState
from transformers.training_args import TrainingArguments
from datetime import datetime
from backend.db import get_db
from backend.models import *
from typing import *
import torch
from backend.enumerate import *
from peft import PeftModelForCausalLM
from transformers import AutoTokenizer
from bert_score import score
import numpy as np
from transformers.utils.dummy_pt_objects import StoppingCriteria
from backend.tuner.generate_prompt import generate_prompt, get_reference_output
from nltk.translate.bleu_score import corpus_bleu
from nltk.util import ngrams
from collections import Counter
from time import time
from tqdm import tqdm
import os
import pickle
import transformers
import time
import json
from backend.evaluate import evaluate
from backend.const import NAN_MAGIC


def openllm(openllmRequest):
    headers = {
        "Content-Type": "application/json"
    }
    requests.post('http://localhost:8000/openllm', json=openllmRequest, headers=headers)

class ReportCallback(TrainerCallback):
    id: int
    indexes: List[Literal["F", "R", "P", "A", "B", "D"]]
    eval_dataset: Any
    enabled: bool = False
    identifier: str
    public: bool
    task_name: str
    task_description: str
    base_model_name: str

    def __init__(
        self,
        finetune_id: int,
        ds_type: int,
        indexes: List[Literal["F", "R", "P", "A", "B", "D"]],
        identifier: str,
        public: bool,
        task_name: str,
        task_description: str,
        base_model_name: str,
    ):
        super().__init__()
        self.id = finetune_id
        self.indexes = indexes
        self.ds_type = ds_type
        if (
            os.environ.get("LOCAL_RANK") is None
            or int(os.environ.get("LOCAL_RANK")) == 0
        ):
            self.enabled = True
            self.identifier = identifier
            self.public = public
            self.task_name = task_name
            self.task_description = task_description
            self.base_model_name = base_model_name

    def set_eval_dataset(self, ds: Any):
        self.eval_dataset = ds

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
        if not self.enabled:
            return
        last_history = state.log_history[-1]
        db = get_db()
        try:
            if all(
                k in last_history for k in ["loss", "learning_rate", "epoch", "step"]
            ):
                loss = last_history["loss"]
                learning_rate = last_history["learning_rate"]
                epoch = last_history["epoch"]
                step = last_history["step"]
                db.add(
                    FtLoggingRecord(
                        entry_id=self.id,
                        loss=loss if not np.isnan(loss) else NAN_MAGIC,
                        learning_rate=learning_rate,
                        epoch=epoch,
                        step=step,
                    )
                )
                db.commit()
            elif all(
                k in last_history
                for k in [
                    "eval_loss",
                    "eval_runtime",
                    "eval_samples_per_second",
                    "eval_steps_per_second",
                    "epoch",
                ]
            ):
                loss = last_history["eval_loss"]
                epoch = last_history["epoch"]
                db.add(FtEvalLossRecord(loss=loss if not np.isnan(loss) else NAN_MAGIC, epoch=epoch, entry_id=self.id))
                db.commit()
        except:
            pass
        finally:
            db.close()

    def on_init_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
        if not self.enabled:
            return
        db = get_db()
        db.add(FinetuneProgress(id=self.id, current=0, total=1))
        db.commit()
        db.close()
        # save validation set
        # if self.eval_dataset is not None:
        #     with open(os.path.join(args.output_dir, "eval_dataset.pkl"), "wb") as f:
        #         pickle.dump(self.eval_dataset, f)

    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
        if not self.enabled:
            return
        db = get_db()
        progress = (
            db.query(FinetuneProgress).filter(FinetuneProgress.id == self.id).first()
        )
        progress.current += 1
        progress.total = state.max_steps
        db.commit()
        db.close()

    def on_train_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
        if not self.enabled:
            return
        db = get_db()
        entry = db.query(FinetuneEntry).filter(FinetuneEntry.id == self.id).first()
        entry.state = FinetuneState.done.value
        entry.end_time = datetime.now()
        adapter = Adapter(
            adapter_name=self.task_name,
            adapter_description=self.task_description,
            ft_entry=self.id,
            base_model_name=self.base_model_name,
            local_path=args.output_dir,
            storage_date=datetime.now(),
            owner=self.identifier,
            public=self.public,
        )
        db.add(adapter)
        # openllmRequest = {
        #     "model_name": self.task_name,
        #     "model_display_name": self.task_name,
        #     "source": "git",
        #     "model_description": self.base_model_name + "-ft",
        #     "download_url": "ft",
        #     "identifier":self.identifier
        # }
        # threading.Thread(
        #     target=openllm, args=(openllmRequest)
        # ).start()
        db.commit()
        db.close()

    def on_evaluate(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
        if not self.enabled:
            return
        db = get_db()
        try:
            if self.eval_dataset is None or len(self.indexes) == 0:
                return
            model: PeftModelForCausalLM = kwargs["model"]
            tokenizer: AutoTokenizer = kwargs["tokenizer"]
            epoch = state.log_history[-1]["epoch"]

            stop_token_ids = [tokenizer.eos_token_id]

            class StopOnTokens(StoppingCriteria):
                def __call__(
                    self,
                    input_ids: torch.LongTensor,
                    scores: torch.FloatTensor,
                    **kwargs
                ) -> bool:
                    for stop_id in stop_token_ids:
                        if input_ids[0][-1] == stop_id:
                            return True
                    return False

            def get_generated_output(data_point):
                prompt = generate_prompt(data_point, self.ds_type, for_infer=True)
                input_ids = tokenizer.encode(prompt, return_tensors="pt").to("cuda")
                output = model.generate(
                    inputs=input_ids,
                    max_length=len(generate_prompt(data_point, self.ds_type)),
                    stopping_criteria=StoppingCriteriaList([StopOnTokens()]),
                )
                out_text = tokenizer.decode(
                    output[0], skip_special_tokens=True
                ).removeprefix(prompt)
                return out_text
            cands = []
            for each in tqdm(self.eval_dataset):
                cands.append(get_generated_output(each))
            refs = [get_reference_output(data_point, self.ds_type) for data_point in self.eval_dataset]

            eval_result = evaluate(self.indexes, refs, cands)

            for k, v in eval_result.items():
                db.add(
                    FtEvalIndexRecord(
                        entry_id=self.id, 
                        name=k, 
                        epoch=epoch, 
                        value=v if not np.isnan(v) else NAN_MAGIC
                    )
                )

            db.commit()
        except Exception as e:
            print(e)
            print("error in on_evaluate")
        finally:
            db.close()
