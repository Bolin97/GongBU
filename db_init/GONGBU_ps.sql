CREATE TABLE pools (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  created_on DATE NOT NULL,
  size INT NOT NULL,
  description TEXT NOT NULL
);

CREATE TABLE dataset_entries (
  id SERIAL PRIMARY KEY,
  pool_id INT NOT NULL,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  type INT NOT NULL,
  created_on DATE NOT NULL,
  size INT NOT NULL,
  FOREIGN KEY (pool_id) REFERENCES pools(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE finetune_entries (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  model_id TEXT NOT NULL,
  dataset_id TEXT NOT NULL,
  devices TEXT NOT NULL,
  eval_indexes TEXT NOT NULL,
  output_dir TEXT NOT NULL,
  adapter_name TEXT NOT NULL,
  batch_size INT NOT NULL,
  micro_batch_size INT NOT NULL,
  num_epochs INT NOT NULL,
  learning_rate FLOAT NOT NULL,
  cutoff_len INT NOT NULL,
  val_set_size INT NOT NULL,
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
  zero_offload BOOLEAN NOT NULL
);

CREATE TABLE eval_index_records (
  id SERIAL PRIMARY KEY,
  entry_id INT NOT NULL,
  name TEXT NOT NULL,
  epoch FLOAT NOT NULL,
  value FLOAT NOT NULL,
  FOREIGN KEY (entry_id) REFERENCES finetune_entries(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE eval_records (
  id SERIAL PRIMARY KEY,
  loss FLOAT NOT NULL,
  epoch FLOAT NOT NULL,
  entry_id INT NOT NULL,
  FOREIGN KEY (entry_id) REFERENCES finetune_entries(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE finetune_datasets (
  id SERIAL PRIMARY KEY,
  entry_id INT NOT NULL,
  content JSON NOT NULL,
  FOREIGN KEY (entry_id) REFERENCES dataset_entries(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE finetune_progresses (
  id INT NOT NULL,
  current INT NOT NULL,
  total INT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES finetune_entries(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE logging_records (
  id SERIAL PRIMARY KEY,
  loss FLOAT NOT NULL,
  learning_rate FLOAT NOT NULL,
  epoch FLOAT NOT NULL,
  step INT NOT NULL,
  entry_id INT NOT NULL,
  FOREIGN KEY (entry_id) REFERENCES finetune_entries(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE open_llms (
  model_id SERIAL PRIMARY KEY,
  model_name TEXT NOT NULL,
  model_description TEXT NOT NULL,
  view_pic TEXT NOT NULL,
  remote_path TEXT NOT NULL,
  local_path TEXT,
  local_store BOOLEAN NOT NULL,
  storage_state TEXT,
  storage_date DATE
);

CREATE TABLE signals (
  id SERIAL PRIMARY KEY,
  receiver TEXT NOT NULL,  -- Assuming receiver is of type TEXT
  signal INT NOT NULL,
  entry_id INT NOT NULL
);