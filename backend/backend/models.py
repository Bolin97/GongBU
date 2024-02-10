from sqlalchemy import Column, Integer, String, Boolean, Date, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime, Float, NullType
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

LIST_SEPERATER = "|"


class OpenLLM(Base):
    __tablename__ = "OPENLLMS"

    model_id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    model_description = Column(String(100), nullable=False)
    view_pic = Column(String(100), nullable=False)
    remote_path = Column(String(100), nullable=False)
    local_path = Column(String(100))
    local_store = Column(TINYINT(1), nullable=False)
    lora_support = Column(TINYINT(1), nullable=False)
    lora_multi_device = Column(TINYINT(1), nullable=False)
    prefix_tuning_support = Column(TINYINT(1), nullable=False)
    prefix_tuning_multi_device = Column(TINYINT(1), nullable=False)
    ptuning_support = Column(TINYINT(1), nullable=False)
    ptuning_multi_device = Column(TINYINT(1), nullable=False)
    prompt_tuning_support = Column(TINYINT(1), nullable=False)
    prompt_tuning_multi_device = Column(TINYINT(1), nullable=False)
    IA3_support = Column(TINYINT(1), nullable=False)
    IA3_multi_device = Column(TINYINT(1), nullable=False)
    storage_state = Column(String(100))
    storage_date = Column(Date)
    finetune = Column(TINYINT(1), nullable=False)
    deployment = Column(TINYINT(1), nullable=False)


class Pool(Base):
    __tablename__ = "POOLS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    creation_date = Column(Date, nullable=False)
    size = Column(Integer, nullable=False)
    description = Column(String(100), nullable=False)

    entries = relationship("DatasetEntry", backref="pool", cascade="all,delete-orphan")


class DatasetEntry(Base):
    __tablename__ = "DATASETENTRIES"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pool_id = Column(Integer, ForeignKey("POOLS.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(100), nullable=False)
    type = Column(Integer, nullable=False)
    creation_date = Column(Date, nullable=False)
    size = Column(Integer, nullable=False)

    finetune_datasets = relationship(
        "FinetuneDataset",
        backref="dataset_entry",
        cascade="all,delete-orphan",
        single_parent=True,
    )


class FinetuneDataset(Base):
    __tablename__ = "FINETUNEDATASETS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(Integer, ForeignKey("DATASETENTRIES.id"), nullable=False)
    content = Column(JSON, nullable=False)


class FinetuneEntry(Base):
    __tablename__ = "FINETUNEENTRIES"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    model_id = Column(String, nullable=False)
    dataset_id = Column(String, nullable=False)
    devices = Column(Text, nullable=False)
    eval_indexes = Column(Text, nullable=False)
    output_dir = Column(String, nullable=False)
    adapter_name = Column(String, nullable=False)
    batch_size = Column(Integer, nullable=False)
    micro_batch_size = Column(Integer, nullable=False)
    num_epochs = Column(Integer, nullable=False)
    learning_rate = Column(Float, nullable=False)
    cutoff_len = Column(Integer, nullable=False)
    val_set_size = Column(Integer, nullable=False)
    use_gradient_checkpointing = Column(Boolean, nullable=False)
    eval_step = Column(Integer, nullable=False)
    save_step = Column(Integer, nullable=False)
    logging_step = Column(Integer, nullable=False)
    lora_r = Column(Float, nullable=False)
    lora_alpha = Column(Float, nullable=False)
    lora_dropout = Column(Float, nullable=False)
    num_virtual_tokens = Column(Integer, nullable=False)
    train_on_inputs = Column(Boolean, nullable=False)
    group_by_length = Column(Boolean, nullable=False)
    bits_and_bytes = Column(Boolean, nullable=False)
    load_8bit = Column(Boolean, nullable=False)
    load_4bit = Column(Boolean, nullable=False)
    llm_int8_threshold = Column(Float, nullable=False)
    llm_int8_enable_fp32_cpu_offload = Column(Boolean, nullable=False)
    llm_int8_has_fp16_weight = Column(Boolean, nullable=False)
    bnb_4bit_compute_dtype = Column(String, nullable=False)
    bnb_4bit_quant_type = Column(String, nullable=False)
    bnb_4bit_use_double_quant = Column(Boolean, nullable=False)
    # 0 running 1 done -1 err
    state = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)

    finetune_datasets = relationship(
        "FinetuneProgress",
        backref="finetune_entry",
        cascade="all,delete-orphan",
        single_parent=True,
    )
    logging_records = relationship(
        "LoggingRecord",
        backref="finetune_entry",
        cascade="all,delete-orphan",
        single_parent=True,
    )
    rating_index_records = relationship(
        "EvalRecord",
        backref="finetune_entry",
        cascade="all,delete-orphan",
        single_parent=True,
    )
    signals = relationship(
        "Signal",
        backref="finetune_entry",
        cascade="all,delete-orphan",
        single_parent=True,
    )


class FinetuneProgress(Base):
    __tablename__ = "FINETUNEPROGRESSES"

    id = Column(Integer, ForeignKey("FINETUNEENTRIES.id"), primary_key=True)
    current = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)


class LoggingRecord(Base):
    __tablename__ = "LOGGINGRECORDS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loss = Column(Float, nullable=False)
    learning_rate = Column(Float, nullable=False)
    epoch = Column(Float, nullable=False)
    step = Column(Integer, nullable=False)
    entry_id = Column(Integer, ForeignKey("FINETUNEENTRIES.id"), primary_key=True)


class EvalIndexRecord(Base):
    __tablename__ = "EVALINDEXRECORDS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    epoch = Column(Float, nullable=False)
    entry_id = Column(Integer, ForeignKey("FINETUNEENTRIES.id"), primary_key=True)


class EvalRecord(Base):
    __tablename__ = "EVALRECORDS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loss = Column(Float, nullable=False)
    epoch = Column(Float, nullable=False)
    entry_id = Column(Integer, ForeignKey("FINETUNEENTRIES.id"), primary_key=True)


class Signal(Base):
    __tablename__ = "SIGNALS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(Integer, ForeignKey("FINETUNEENTRIES.id"), primary_key=True)
    signal = Column(Integer, nullable=False)

class DeployEntry(Base):
    __tablename__ = "DEPLOYENTRIES"

    entry_id = Column(Integer, primary_key=True, autoincrement=True)
    model_or_finetune_id = Column(Integer, nullable=False)
    deploy_finetuned = Column(Boolean, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    params = Column(JSON, nullable=False)
    devices = Column(String(100), nullable=False)
    state = Column(Integer, nullable=False)
    
    deploy_access_counter = relationship("DeployAccessCounter", backref="deploy_entry", cascade="all,delete-orphan", single_parent=True)
    
class DeployAccessCounter(Base):
    __tablename__ = "DEPLOYACCESSCOUNTER"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    entry_id = Column(Integer, ForeignKey("DEPLOYENTRIES.entry_id"), nullable=False)
    count = Column(Integer, nullable=False)
