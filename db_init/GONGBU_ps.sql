CREATE TABLE pools (
    id SERIAL PRIMARY KEY, 
    name TEXT NOT NULL, 
    created_on DATE NOT NULL, 
    size INT NOT NULL, 
    description TEXT NOT NULL,
    owner TEXT NOT NULL,
    public BOOLEAN NOT NULL
);

CREATE TABLE dataset_entries (
    id SERIAL PRIMARY KEY, 
    pool_id INT NOT NULL, 
    name TEXT NOT NULL, 
    description TEXT NOT NULL, 
    type INT NOT NULL, 
    created_on DATE NOT NULL, 
    size INT NOT NULL, 
    owner TEXT NOT NULL,
    public BOOLEAN NOT NULL,
    FOREIGN KEY (pool_id) REFERENCES pools (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE finetune_entries (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  display_name TEXT NOT NULL
  model_id TEXT NOT NULL,
  dataset_id TEXT NOT NULL,
  devices TEXT[] NOT NULL,
  eval_indexes TEXT[] NOT NULL,
  output_dir TEXT NOT NULL,
  adapter_name TEXT NOT NULL,
  batch_size INT NOT NULL,
  micro_batch_size INT NOT NULL,
  num_epochs INT NOT NULL,
  learning_rate FLOAT NOT NULL,
  cutoff_len INT NOT NULL,
  val_set_size FLOAT NOT NULL,
  use_gradient_checkpointing BOOLEAN NOT NULL,
  eval_step INT NOT NULL,
  save_step INT NOT NULL,
  logging_step INT NOT NULL,
  lora_r INT NOT NULL,
  lora_alpha FLOAT NOT NULL,
  lora_dropout FLOAT NOT NULL,
  num_virtual_tokens INT NOT NULL,
  train_on_inputs BOOLEAN NOT NULL,
  group_by_length BOOLEAN NOT NULL,
  bits_and_bytes BOOLEAN NOT NULL,
  load_8bit BOOLEAN NOT NULL,
  load_4bit BOOLEAN NOT NULL,
  llm_int8_threshold FLOAT NOT NULL,
  llm_int8_enable_fp32_cpu_offload BOOLEAN NOT NULL,
  llm_int8_has_fp16_weight BOOLEAN NOT NULL,
  bnb_4bit_compute_dtype TEXT NOT NULL,
  bnb_4bit_quant_type TEXT NOT NULL,
  bnb_4bit_use_double_quant BOOLEAN NOT NULL,
  state INTEGER NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  zero_optimization BOOLEAN NOT NULL,
  zero_stage INT NOT NULL,
  zero_offload BOOLEAN NOT NULL,
  use_dora BOOLEAN NOT NULL,
  use_rslora BOOLEAN NOT NULL,
  rank_dropout FLOAT NOT NULL,
  module_dropout FLOAT NOT NULL,
  use_effective_conv2d BOOLEAN NOT NULL,
  use_flash_attention BOOLEAN NOT NULL,
  adapter_id INT,
  owner TEXT NOT NULL,
  public BOOLEAN NOT NULL
);

CREATE TABLE ft_eval_index_records (
    id SERIAL PRIMARY KEY, 
    entry_id INT NOT NULL, 
    name TEXT NOT NULL, 
    epoch FLOAT NOT NULL, 
    value FLOAT NOT NULL, 
    FOREIGN KEY (entry_id) REFERENCES finetune_entries (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE ft_eval_loss_records (
    id SERIAL PRIMARY KEY, 
    loss FLOAT NOT NULL, 
    epoch FLOAT NOT NULL, 
    entry_id INT NOT NULL, 
    FOREIGN KEY (entry_id) REFERENCES finetune_entries (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE finetune_datasets (
    id SERIAL PRIMARY KEY, 
    entry_id INT NOT NULL, 
    content JSON NOT NULL, 
    owner TEXT NOT NULL,
    public BOOLEAN NOT NULL,
    FOREIGN KEY (entry_id) REFERENCES dataset_entries (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE finetune_progresses (
    id INT NOT NULL, 
    current INT NOT NULL,
    total INT NOT NULL, 
    PRIMARY KEY (id), FOREIGN KEY (id) REFERENCES finetune_entries (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE ft_logging_records (
    id SERIAL PRIMARY KEY, 
    loss FLOAT NOT NULL, 
    learning_rate FLOAT NOT NULL, 
    epoch FLOAT NOT NULL, 
    step INT NOT NULL, 
    entry_id INT NOT NULL, 
    FOREIGN KEY (entry_id) REFERENCES finetune_entries (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE open_llms (
    id SERIAL PRIMARY KEY, 
    model_name TEXT NOT NULL, 
    model_description TEXT NOT NULL, 
    view_pic TEXT NOT NULL, 
    remote_path TEXT NOT NULL, 
    local_path TEXT, 
    local_store BOOLEAN NOT NULL, 
    storage_state TEXT, 
    storage_date DATE,
    owner TEXT NOT NULL,
    public BOOLEAN NOT NULL
);

CREATE TABLE adapters (
    id SERIAL PRIMARY KEY, 
    base_model_name TEXT NOT NULL,
    adapter_name TEXT NOT NULL, 
    adapter_description TEXT NOT NULL, 
    local_path TEXT, 
    storage_date DATE,
    owner TEXT NOT NULL,
    public BOOLEAN NOT NULL
);

CREATE TABLE signals (
    id SERIAL PRIMARY KEY, receiver TEXT NOT NULL,
    signal INT NOT NULL, entry_id INT NOT NULL,
    owner TEXT NOT NULL,
    public BOOLEAN NOT NULL
);

CREATE TABLE users (
    identifier TEXT NOT NULL PRIMARY KEY, password TEXT NOT NULL
);

CREATE TABLE faults (
    id SERIAL PRIMARY KEY, 
    time TIMESTAMP NOT NULL,
    source TEXT[] NOT NULL, 
    message TEXT NOT NULL, 
    code INT NOT NULL,
    owner TEXT NOT NULL,
    public BOOLEAN NOT NULL
);

CREATE TABLE fault_logs (
    id SERIAL PRIMARY KEY,
    fault_id INT NOT NULL,
    log_content TEXT NOT NULL,
    FOREIGN KEY (fault_id) REFERENCES faults (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE deployments (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    state INT NOT NULL,
    model_or_adapter_id INT NOT NULL,
    deploy_base_model BOOLEAN NOT NULL,
    bits_and_bytes BOOLEAN NOT NULL,
    load_8bit BOOLEAN NOT NULL,
    load_4bit BOOLEAN NOT NULL,
    use_flash_attention BOOLEAN NOT NULL,
    use_deepspeed BOOLEAN NOT NULl,
    devices TEXT[] NOT NULL,
    port INT NOT NULL,
    owner TEXT NOT NULL,
    public BOOLEAN NOT NULL
);

CREATE TABLE evaluations (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    state INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    model_or_adapter_id INT NOT NULL,
    deploy_base_model BOOLEAN NOT NULL,
    bits_and_bytes BOOLEAN NOT NULL,
    load_8bit BOOLEAN NOT NULL,
    load_4bit BOOLEAN NOT NULL,
    use_flash_attention BOOLEAN NOT NULL,
    use_deepspeed BOOLEAN NOT NULl,
    devices TEXT[] NOT NULL,
    indexes TEXT[] NOT NULL,
    dataset_id INT NOT NULL,
    val_set_size FLOAT NOT NULL,
    result JSON,
    owner TEXT NOT NULL,
    public BOOLEAN NOT NULL
);

CREATE TABLE evaluation_data (
    id SERIAL PRIMARY KEY,
    entry_id INT NOT NULL,
    content JSON NOT NULL,
    FOREIGN KEY (entry_id) REFERENCES evaluations (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE evaluation_generation (
    id SERIAL PRIMARY KEY,
    entry_id INT NOT NULL,
    content JSON NOT NULL,
    FOREIGN KEY (entry_id) REFERENCES evaluations (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE evaluation_progresses (
    id SERIAL PRIMARY KEY, 
    entry_id INT NOT NULL,
    current INT NOT NULL,
    total INT NOT NULL, 
    FOREIGN KEY (entry_id) REFERENCES evaluations (id) ON DELETE CASCADE ON UPDATE CASCADE
);