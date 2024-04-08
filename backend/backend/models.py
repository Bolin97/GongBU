from sqlalchemy import Column, DateTime, Integer, String, Date, Float, Boolean, ForeignKey, JSON, TIMESTAMP
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Pool(Base):
    __tablename__ = 'pools'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_on = Column(Date, nullable=False)
    size = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    public = Column(Boolean, nullable=False)

class DatasetEntry(Base):
    __tablename__ = 'dataset_entries'
    id = Column(Integer, primary_key=True)
    pool_id = Column(Integer, ForeignKey('pools.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    type = Column(Integer, nullable=False)
    created_on = Column(Date, nullable=False)
    size = Column(Integer, nullable=False)
    owner = Column(String, nullable=False)
    public = Column(Boolean, nullable=False)

class FinetuneEntry(Base):
    __tablename__ = 'finetune_entries'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    model_id = Column(String, nullable=False)
    dataset_id = Column(Integer, ForeignKey('dataset_entries.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    devices = Column(ARRAY(String, dimensions=1), nullable=False)
    eval_indexes = Column(ARRAY(String, dimensions=1), nullable=False)
    eval_indexes = Column(String, nullable=False)
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
    lora_r = Column(Integer, nullable=False)
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
    state = Column(Integer, nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP)
    zero_optimization = Column(Boolean, nullable=False)
    zero_stage = Column(Integer, nullable=False)
    zero_offload = Column(Boolean, nullable=False)
    use_dora = Column(Boolean, nullable=False)
    use_rslora = Column(Boolean, nullable=False)
    rank_dropout = Column(Float, nullable=False)
    module_dropout = Column(Float, nullable=False)
    use_effective_conv2d = Column(Boolean, nullable=False)
    use_flash_attention = Column(Boolean, nullable=False)
    owner = Column(String, nullable=False)
    public = Column(Boolean, nullable=False)

class EvalIndexRecord(Base):
    __tablename__ = 'eval_index_records'
    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey('finetune_entries.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    epoch = Column(Float, nullable=False)
    value = Column(Float, nullable=False)

class EvalRecord(Base):
    __tablename__ = 'eval_records'
    id = Column(Integer, primary_key=True)
    loss = Column(Float, nullable=False)
    epoch = Column(Float, nullable=False)
    owner = Column(String, nullable=False)
    public = Column(Boolean, nullable=False)
    entry_id = Column(Integer, ForeignKey('finetune_entries.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

class FinetuneDataset(Base):
    __tablename__ = 'finetune_datasets'
    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey('dataset_entries.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    content = Column(JSON, nullable=False)
    owner = Column(String, nullable=False)
    public = Column(Boolean, nullable=False)

class FinetuneProgress(Base):
    __tablename__ = 'finetune_progresses'
    id = Column(Integer, ForeignKey('finetune_entries.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    current = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)

class LoggingRecord(Base):
    __tablename__ = 'logging_records'
    id = Column(Integer, primary_key=True)
    loss = Column(Float, nullable=False)
    learning_rate = Column(Float, nullable=False)
    epoch = Column(Float, nullable=False)
    step = Column(Integer, nullable=False)
    entry_id = Column(Integer, ForeignKey('finetune_entries.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

class OpenLLM(Base):
    __tablename__ = 'open_llms'
    model_id = Column(Integer, primary_key=True)
    model_name = Column(String, nullable=False)
    model_description = Column(String, nullable=False)
    view_pic = Column(String, nullable=False)
    remote_path = Column(String, nullable=False)
    local_path = Column(String)
    local_store = Column(Boolean, nullable=False)
    storage_state = Column(String)
    storage_date = Column(Date)
    owner = Column(String, nullable=False)
    public = Column(Boolean, nullable=False)

class Signal(Base):
    __tablename__ = 'signals'
    id = Column(Integer, primary_key=True)
    receiver = Column(String, nullable=False)
    signal = Column(Integer, nullable=False)
    entry_id = Column(Integer, nullable=False)
    owner = Column(String, nullable=False)
    public = Column(Boolean, nullable=False)

class User(Base):
    __tablename__ = 'users'
    identifier = Column(String, nullable=False, primary_key=True)
    password = Column(String, nullable=False)

class Fault(Base):
    __tablename__ = 'faults'
    id = Column(Integer, primary_key=True)
    time = Column(TIMESTAMP, nullable=False)
    source = Column(ARRAY(String, dimensions=1), nullable=False)
    message = Column(String, nullable=False)
    code = Column(Integer, nullable=False)
    owner = Column(String, nullable=False)
    public = Column(Boolean, nullable=False)

class FaultLog(Base):
    __tablename__ = 'fault_logs'
    id = Column(Integer, primary_key=True)
    fault_id = Column(Integer, ForeignKey('faults.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    log_content = Column(String, nullable=False)
