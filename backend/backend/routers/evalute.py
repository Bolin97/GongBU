# 实现一下模型评测页面
# main.py
from collections import defaultdict
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime
import requests
from sqlalchemy import  and_
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.models import *
from backend.auth import *
from fastapi.params import Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm.session import Session
from backend.db import gen_db, get_db

evalute_router = APIRouter()


class EvaluationRequest(BaseModel):
    model_name: str
    owner: str
    model_id: int
    task_type: str  # translation/qa/summarization

class MetricResult(BaseModel):
    metric_name: str
    score: float

# 假设已经定义的数据库模型
class ModelEvaluation(BaseModel):
    model_name: str
    task_type: str
    metrics: list
    summary_score: float
    timestamp: datetime

# 完成请求模型
class EvaluationInformerRequest(BaseModel):
    evaluation_id: int
    eval_result_id: int

# 评估响应模型
class EvaluationResponse(BaseModel):
    task_id: str
    timestamp: datetime
    model_name: str
    task_type: str
    metrics: list
    summary_score: float

class EvaluationResultResponse(BaseModel):
    id: int
    model_name: str
    task_type: str
    summary_score: float
    created_at: datetime
    username: str


metric_mapping = {
    "translation": {
        "P": "Precision",
        "R": "Recall",
        "F": "F1-Score",
        "B": "BLEU"
    },
    "qa" : {
        "R": "Recall",
        "F": "F1-Score",
        "A": "Accuracy"
    },
    "text_generation": {
        "B": "BLEU",
        "P": "Precision",
        "D": "Distinct-2"
    },
    "summarization": {
        "R": "Recall",
        "F": "F1-Score",
        "P": "Precision",
        "D": "Distinct-2"
    },
    "classification": {
        "P": "Precision",
        "R": "Recall",
        "F": "F1-Score",
        "A": "Accuracy"
    }
}

def normalize_metrics(task_type: str, raw_result: dict):
    """增强型标准化处理，支持动态字段映射"""

    # 获取当前任务类型的字段映射
    field_map = metric_mapping.get(task_type, {})
    
    dictTemp = {}
    # 构建标准化指标结果
    normalized = []
    for raw_key, value in raw_result.items():

        if raw_key not in field_map:
            continue
        # 映射指标名称
        metric_name = field_map.get(raw_key, raw_key)
        dictTemp[metric_name] = value
        
        normalized.append(MetricResult(
            metric_name=metric_name,
            score=round(float(value), 4),
        ))
    return calculate_summary(normalized), dictTemp



def calculate_summary(metrics: List[MetricResult]) -> float:
    """动态权重策略（新增指标权重）"""
    dynamic_weights = {
        # 基础指标
        "BLEU": 0.4,
        "TER": 0.3,
        # 问答类
        "Accuracy": 0.6,
        "Recall": 0.5,
        "F1-Score": 0.7,
        # 生成类
        "Distinct-2": 0.4,
        "ROUGE-L": 0.5
    }
    # 自动处理未知指标（默认权重0.5）
    total = sum(dynamic_weights.get(m.metric_name, 0.5) * m.score for m in metrics)
    weight_sum = sum(dynamic_weights.get(m.metric_name, 0.5) for m in metrics)
    return total / weight_sum if weight_sum > 0 else 0


def getDatasetId(task_type):
    if task_type == "translation":
        return 4
    if task_type == "qa":
        return 3
    if task_type == "text_generation":
        return 5
    if task_type == "classification":
        return 7
    if task_type == "summarization":
        return 6
    return -1


@evalute_router.post("/informer")
async def informer(
    request: EvaluationInformerRequest,
    db: Session = Depends(get_db)
):
    try:
        # 获取评估记录
        entry = db.query(Evaluation).filter(Evaluation.id == request.evaluation_id).first()
        evaluationResult = db.query(EvaluationResult).filter(EvaluationResult.id == request.eval_result_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        if not evaluationResult:
            raise HTTPException(status_code=404, detail="EvaluationResult not found")
        
        # 标准化评估结果
        try:
            summary_score, result = normalize_metrics(evaluationResult.task_type, entry.result)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        
        # 更新综合得分
        evaluationResult.summary_score = summary_score
        evaluationResult.content = result
        
        db.commit()
        
        return {
            "result_id": evaluationResult.id,
            "summary": summary_score,
            "metrics": result
        } 
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@evalute_router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_model(
    request: EvaluationRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_identifier),
    token: str = Depends(oauth2_scheme)
):
    
    
    eval_result = EvaluationResult(
        model_name=request.model_name,
        owner = request.owner,
        task_type=request.task_type,
        username=username
    )
    db.add(eval_result)
    db.commit()
    url = "http://backend:8000/eval"
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    query_params = {
        "name": f"{request.model_name}模型{request.task_type}评估任务",
        "description": "开发者社区模型评估"
    }
    url = url  + "?" + "&".join(f"{k}={v}" for k, v in query_params.items())
    payload = {
        "model_or_adapter_id": request.model_id,
        "deploy_base_model": True,
        "bits_and_bytes": False,
        "load_8bit": True,
        "load_4bit": False,
        "use_flash_attention": False,
        "use_deepspeed": False,
        "devices": ['auto'],
        "indexes": list(metric_mapping[request.task_type].keys()),
        "dataset_id": getDatasetId(request.task_type),
        "val_set_size": 0.5,
        "eval_result_id":eval_result.id
    }

    response = requests.post(url, json=payload, headers=headers)
    eval_result.eval_id = response.json()
    
    db.commit()
    response = EvaluationResponse(
        task_id= eval_result.id,
        created_at=eval_result.created_at,
        model_name=request.model_name,
        task_type=request.task_type,
    )
    
    return response


@evalute_router.get("/evaluations/{owner}/{model_name}")
async def get_evaluations_by_model(
    owner:str,
    model_name: str,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_identifier)
):
    """
    获取指定模型且包含总分的评估结果
    """
    model = accessible1(db.query(OpenLLM).filter(OpenLLM.model_name==model_name, OpenLLM.owner==owner), username).first()
    if not model:
        return {"error": "Model not found or access denied."}

    results = db.query(EvaluationResult).filter(
        EvaluationResult.model_name == model_name,
        EvaluationResult.owner == owner,
        EvaluationResult.summary_score.isnot(None)
    ).all()

    task_data = defaultdict(lambda: {"metrics": []})

    for result in results:
        # 假设 content 字段是一个 dict，包含多个指标名和数值
        for metric_name, value in result.content.items():
            task_data[result.task_type]["metrics"].append({
                "name": metric_name,
                "value": value
            })

    return task_data

@evalute_router.get("/models")
async def get_all_eval_models(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_identifier)
):
    models = accessible1( 
        db.query(OpenLLM), username
    ).all()
    return [
        {"model_name": m.model_name, "id": m.id, "owner": m.owner}
        for m in models
    ]

# 需要分类返回
@evalute_router.get("/evaluations")
async def get_all_evaluations(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_identifier)
):
   # 获取当前用户可访问的模型（model_name, owner）
    allowed_models =  accessible1(db.query(OpenLLM), username).subquery()

    # 查询匹配的评估结果
    results = db.query(EvaluationResult).join(
        allowed_models,
        and_(
            EvaluationResult.model_name == allowed_models.c.model_name,
            EvaluationResult.owner == allowed_models.c.owner
        )
    ).filter(EvaluationResult.summary_score.isnot(None)).order_by(
    EvaluationResult.summary_score.desc()).all()

    # Metric 映射（key为任务类型，值为评估指标缩写）
    metric_mapping = {
        "translation": ["B", "R", "P"],
        "qa": ["A", "F", "R"],
        "text_generation": ["B", "P", "D"],
        "classification": ["A", "F", "P", "R"]
    }

    # 缩写 -> 中文标签
    metric_labels = {
        "P": "Precision",
        "R": "Recall",
        "F": "F1-Score",
        "B": "BLEU",
        "A": "Accuracy",
        "D": "Distinct-2"
    }

    # 当你访问一个不存在的 key 时，它会自动创建一个默认值
    task_output = defaultdict(lambda: {"metrics": [], "data": []})

    for result in results:
        task = result.task_type
        model = result.model_name
        summary_score = result.summary_score
        content = result.content or {}

        metrics = metric_mapping.get(task, [])
        if not task_output[task]["metrics"]:
            task_output[task]["metrics"] = [metric_labels[m] for m in metrics]

        entry = {"model": model}
        entry['summary'] = summary_score
        for m in metrics:
            label = metric_labels[m]
            entry[label] = content.get(label)  # JSON 中的 key 就是标签

        task_output[task]["data"].append(entry)

    return task_output

