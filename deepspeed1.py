# # 比较使用deepspeed和accelerate的训练效率
# """
# 下面是使用deepspeed
# """

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from peft import LoraConfig, get_peft_model
from datasets import load_dataset, DatasetDict
from transformers import TrainingArguments, Trainer
import os

from transformers import AutoTokenizer
from torch.amp import GradScaler

scaler = GradScaler("cuda")


# 加载 BERT 模型和分词器
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)  # 情感分类任务

# 配置 LoRA（应用于注意力层的 query 和 value 投影）
lora_config = LoraConfig(
    r=8,  # 低秩矩阵的维度
    lora_alpha=32,
    target_modules=["query", "value"],  # BERT 注意力层的模块名称
    lora_dropout=0.05,
    bias="none",
    task_type="SEQ_CLS"
)

# 应用 LoRA 到模型
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # 输出可训练参数占比（通常 <1%）



# 加载 IMDb 情感分析数据集
dataset = load_dataset("imdb")
# dataset = DatasetDict({k: v.shuffle().select(range(1920)) for k, v in dataset.items()}) 

print("切片后数据集:", dataset)
# 分词处理函数
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=512,
        padding="max_length"
    )

# 数据预处理
small_train_dataset = dataset["train"].select(range(1920))  # 训练集取前100条
small_test_dataset = dataset["test"].select(range(960))     # 测试集取前20条（可选）
# dataset.train_test_split(test_size=0.3, seed=42)
# tokenized_dataset = dataset.map(tokenize_function, batched=True)
# tokenized_dataset = tokenized_dataset.rename_column("label", "labels")  # 对齐标签字段
tokenized_train = small_train_dataset.map(tokenize_function, batched=True)
tokenized_test = small_test_dataset.map(tokenize_function, batched=True)


# 训练参数配置
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=8,  # 单 GPU 批次大小
    gradient_accumulation_steps=4,   # 梯度累积模拟更大批次
    learning_rate=3e-4,
    logging_steps=50,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    report_to="none",
    fp16=True,
    weight_decay=0.01,  
    deepspeed="./ds_config.json"  # 加载 DeepSpeed 配置
)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# 初始化 Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test
)

# 启动训练
trainer.train()




# # 加载微调后的模型
# from peft import PeftModel
# tokenizer = AutoTokenizer.from_pretrained("./results/checkpoint-60")
# model = PeftModel.from_pretrained("./results/checkpoint-60")

# # 单条文本预测样例
# text = "This movie is fantastic! The plot is thrilling."
# inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
# outputs = model(**inputs)
# predicted_label = outputs.logits.argmax().item()  # 0=负面，1=正面
# print(f"预测结果: {'正面' if predicted_label else '负面'}")


# eval_results = trainer.evaluate()
# print(f"验证集准确率: {eval_results['eval_accuracy']:.2f}")