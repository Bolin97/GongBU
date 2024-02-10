from transformers import TrainerCallback
from transformers.generation.stopping_criteria import StoppingCriteriaList
from transformers.trainer_callback import TrainerControl, TrainerState
from transformers.training_args import TrainingArguments
import datetime
from backend.db import get_db
from backend.models import *
from typing import *
import torch
from peft import PeftModelForCausalLM
from transformers import AutoTokenizer
from bert_score import score
import numpy as np
from transformers.utils.dummy_pt_objects import StoppingCriteria
from .generate_prompt import generate_prompt
from nltk.translate.bleu_score import corpus_bleu
import jieba
from nltk.util import ngrams
from collections import Counter
from time import time
from backend.sync import ctx

class ReportCallback(TrainerCallback):
    id: int
    indexes: List[Literal["F", "R", "P", "A", "B", "D"]]
    eval_dataset: Any
    first_device: int

    def __init__(
        self, finetune_id: int, first_device: int, indexes: List[Literal["F", "R", "P", "A", "B", "D"]]
    ):
        super().__init__()
        self.id = finetune_id
        self.indexes = indexes
        self.first_device = first_device

    def set_eval_dataset(self, ds: Any):
        self.eval_dataset = ds

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
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
                    LoggingRecord(
                        entry_id=self.id,
                        loss=loss,
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
                db.add(EvalRecord(loss=loss, epoch=epoch, entry_id=self.id))
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
        db = get_db()
        db.add(FinetuneProgress(id=self.id, current=0, total=1))
        db.commit()
        db.close()

    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
        db = get_db()
        progress = (
            db.query(FinetuneProgress).filter(FinetuneProgress.id == self.id).first()
        )
        progress.current += 1
        progress.total = state.max_steps
        db.commit()

        signals = db.query(Signal).filter(Signal.entry_id == self.id).all()

        # 0 for stop
        if len(signals) > 0 and signals[0].signal == 0:
            control.should_save = 1
            control.should_training_stop = 1
            db.delete(signals)
            db.commit()
        db.close()

    def on_train_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
        db = get_db()
        # 0 training 1 done -1 error
        entry = db.query(FinetuneEntry).filter(FinetuneEntry.id == self.id).first()
        entry.state = 1
        entry.end_time = datetime.datetime.now()
        db.commit()
        db.close()
    

    def on_evaluate(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
        if self.eval_dataset is None or len(self.indexes) == 0:
            return
        model: PeftModelForCausalLM = kwargs["model"]
        tokenizer: AutoTokenizer = kwargs["tokenizer"]
        epoch = state.log_history[-1]["epoch"]

        stop_token_ids = [tokenizer.eos_token_id]
        class StopOnTokens(StoppingCriteria):
            def __call__(
                self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs
            ) -> bool:
                for stop_id in stop_token_ids:
                    if input_ids[0][-1] == stop_id:
                        return True
                return False
        
        def get_generated_output(data_point):
            prompt = generate_prompt(data_point, for_infer=True)
            input_ids = tokenizer.encode(prompt, return_tensors="pt").to(f"cuda:{self.first_device}")
            output = model.generate(inputs=input_ids, max_length=len(generate_prompt(data_point)), stopping_criteria=StoppingCriteriaList([StopOnTokens()]))
            out_text = tokenizer.decode(output[0], skip_special_tokens=True).removeprefix(prompt)
            return out_text

        db = get_db()
        cands = list(map(get_generated_output, self.eval_dataset))
        refs = list(map(lambda data_point: data_point["output"], self.eval_dataset))
        # cands = list(np.vectorize(get_generated_output)(self.eval_dataset))
        # refs = list(map(lambda data_point: data_point["output"], self.eval_dataset))
        if any(ind in self.indexes for ind in ["P", "R", "F"]):
            P, R, F = score(
                cands, refs, model_type="bert-base-chinese", lang="zh", verbose=True
            )
            db.add(
                EvalIndexRecord(
                    name="P", value=P.mean().item(), epoch=epoch, entry_id=self.id
                )
            )
            db.add(
                EvalIndexRecord(
                    name="R", value=R.mean().item(), epoch=epoch, entry_id=self.id
                )
            )
            db.add(
                EvalIndexRecord(
                    name="F", value=F.mean().item(), epoch=epoch, entry_id=self.id
                )
            )
        if "A" in self.indexes:
            def remove_blank(s):
                return s.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", "").replace("　", "")
            db.add(
                EvalIndexRecord(
                    name="A",
                    value=sum([1 for c, r in zip(list(map(remove_blank, cands)), list(map(remove_blank, refs))) if c == r]) / len(cands),
                    epoch=epoch,
                    entry_id=self.id,
                )
            )
        if "B" in self.indexes:
            cands_b = [jieba.lcut(sent) for sent in cands]
            refs_b = [jieba.lcut(sent) for sent in refs]
            db.add(
                EvalIndexRecord(
                    name="B",
                    value=corpus_bleu(refs_b, cands_b),
                    epoch=epoch,
                    entry_id=self.id,
                )
            )
        if "D" in self.indexes:

            def calculate_distinct_n(text):
                n = 2
                # Split the text into words
                words = jieba.lcut(text)

                # Calculate n-grams
                n_grams = list(ngrams(words, n))

                # Count distinct n-grams
                distinct_ngrams = len(Counter(n_grams))

                # Calculate distinct-n
                distinct_n = distinct_ngrams / len(n_grams) if len(n_grams) > 0 else 0

                return distinct_n

            db.add(
                EvalIndexRecord(
                    name="D",
                    value=np.vectorize(calculate_distinct_n)(cands).mean(),
                    epoch=epoch,
                    entry_id=self.id,
                )
            )
        db.commit()
        db.close()
