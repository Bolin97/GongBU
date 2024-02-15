import json
from bert_score import score
import gradio as gr
import gradio_client as grc
import jieba
from nltk.translate.bleu_score import corpus_bleu
import jieba
from nltk.util import ngrams
from collections import Counter
from backend.tuner.generate_prompt import generate_prompt
import numpy as np
from backend.deployment.deployment_manager import LLMWrapper

"""from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
	# str  in 'Message' Textbox component
	"Hello!!",	
	# float (numeric value between 0.1 and 3.0) in 'Temperature' Slider component
	0.1,
	# float (numeric value between 10 and 100) in 'Max Length' Slider component
	10,	
	api_name="/chat"
)
print(result)"""

class Main:
    
    llm: LLMWrapper
    port: int
    
    def __init__(self, llm: LLMWrapper, port: int):
        self.llm = llm
        self.port = port
    
    def get_startup_info(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    @staticmethod
    def get_id() -> str:
        return "Evaluation"
    
    @staticmethod
    def get_name() -> str:
        return "Evaluation"
    
    @staticmethod
    def get_description() -> str:
        return "Evaluation for llm"
    
    def get_generated_output(self, data_point):
        prompt = generate_prompt(data_point, for_infer=True)
        result = self.llm.text_generate(
            prompt,
            len(generate_prompt(data_point)),
            temperature=0.2
        )
        return result

    def remove_blank(self, s):
        return s.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", "").replace("　", "")

    def calculate_distinct_n(self, text):
        n = 2
        words = jieba.lcut(text)
        n_grams = list(ngrams(words, n))
        distinct_ngrams = len(Counter(n_grams))
        distinct_n = distinct_ngrams / len(n_grams) if len(n_grams) > 0 else 0
        return distinct_n

    def eval(self, file_binary):
        if file_binary is None:
            return {"error": "No file uploaded"}
        dataset = file_binary.decode("utf-8")
        eval_dataset = json.loads(dataset)
        cands = list(map(self.get_generated_output, eval_dataset))
        refs = list(map(lambda data_point: data_point["output"], eval_dataset))
        P, R, F = score(cands, refs, model_type="bert-base-chinese", lang="zh", verbose=True)
        A = sum([1 for c, r in zip(list(map(self.remove_blank, cands)), list(map(self.remove_blank, refs))) if c == r]) / len(cands)
        cands_b = [jieba.lcut(sent) for sent in cands]
        refs_b = [jieba.lcut(sent) for sent in refs]
        B = corpus_bleu(refs_b, cands_b)
        D = np.vectorize(self.calculate_distinct_n)(cands).mean()
        return {"P": P, "R": R, "F": F, "A": A, "B": B, "D": D}

    def run(self):
        iface = gr.Interface(fn=self.eval, inputs=gr.File(label="Upload a validation datatset", type="binary"), outputs="json")
        iface.launch(server_port=self.port)