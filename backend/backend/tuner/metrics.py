# from typing import *

# from transformers.trainer_utils import EvalPrediction
# from transformers import PreTrainedTokenizer

# OOM, WHY??
# def get_compute_metrics_func(
#     indexes: List[Literal["F", "R", "P", "A", "B", "D"]],
#     tokenizer: PreTrainedTokenizer
# ) -> Callable[[EvalPrediction], Dict]:
    
#     if indexes is None or len(indexes) == 0:
#         return None
    
#     def compute_metrics(p: EvalPrediction) -> Dict:
#         # ret = evaluate(indexes, refs, cands)
#         return {}

#     return compute_metrics