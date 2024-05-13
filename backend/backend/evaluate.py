from bert_score import score
from nltk.translate.bleu_score import corpus_bleu
import jieba
from nltk.util import ngrams
from collections import Counter
import numpy as np
from backend.const import NAN_MAGIC


def PRF(refs, cands) -> dict[str, float]:
    P, R, F = score(
        cands, refs, model_type="bert-base-chinese", lang="zh", verbose=True
    )
    return {"P": P.mean().item(), "R": R.mean().item(), "F": F.mean().item()}


def D(cands) -> dict[str, float]:
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

    return {"D": np.vectorize(calculate_distinct_n)(cands).mean()}


def A(refs, cands) -> dict[str, float]:
    def remove_blank(s):
        return (
            s.replace(" ", "")
            .replace("\n", "")
            .replace("\t", "")
            .replace("\r", "")
            .replace("　", "")
        )

    return {
        "A": sum(
            [
                1
                for c, r in zip(
                    list(map(remove_blank, cands)), list(map(remove_blank, refs))
                )
                if c == r
            ]
        )
        / len(cands)
    }


def B(refs, cands) -> dict[str, float]:
    cands_b = [jieba.lcut(sent) for sent in cands]
    refs_b = [jieba.lcut(sent) for sent in refs]
    return {"B": corpus_bleu(refs_b, cands_b)}


def evaluate(indexes: list[str], refs: list[str], cands: list[str]) -> dict[str, float]:
    if len(refs) != len(cands):
        raise ValueError("The number of references and candidates should be the same.")

    ret = {}

    if any(i in indexes for i in ["P", "R", "F"]):
        ret.update(PRF(refs, cands))

    if "D" in indexes:
        ret.update(D(cands))

    if "A" in indexes:
        ret.update(A(refs, cands))

    if "B" in indexes:
        ret.update(B(refs, cands))
        
    ret = {k: v if not np.isnan(v) else NAN_MAGIC for k, v in ret.items()}

    return ret
