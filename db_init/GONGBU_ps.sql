-- -- Database export via SQLPro (https://www.sqlprostudio.com/)
-- -- Exported by zend at 06-02-2024 03:33.
-- -- WARNING: This file may contain descructive statements such as DROPs.
-- -- Please ensure that you are running the script at the proper location.

-- -- BEGIN TABLE POOLS
-- CREATE TABLE `POOLS` (
--   `id` int NOT NULL AUTO_INCREMENT,
--   `name` varchar(100) NOT NULL,
--   `creation_date` date NOT NULL,
--   `size` int unsigned NOT NULL,
--   `description` varchar(100) NOT NULL,
--   PRIMARY KEY (`id`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -- END TABLE POOLS

-- -- BEGIN TABLE DATASETENTRIES
-- CREATE TABLE `DATASETENTRIES` (
--   `id` int NOT NULL AUTO_INCREMENT,
--   `pool_id` int NOT NULL,
--   `name` varchar(100) NOT NULL,
--   `description` varchar(100) NOT NULL,
--   `type` int NOT NULL,
--   `creation_date` date NOT NULL,
--   `size` int NOT NULL,
--   PRIMARY KEY (`id`),
--   KEY `DATASETEMTRIES_TO_POOLS` (`pool_id`),
--   CONSTRAINT `DATASETEMTRIES_TO_POOLS` FOREIGN KEY (`pool_id`) REFERENCES `POOLS` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -- END TABLE DATASETENTRIES

-- -- BEGIN TABLE DEPLOYENTRIES
-- CREATE TABLE `DEPLOYENTRIES` (
--   `entry_id` int NOT NULL AUTO_INCREMENT,
--   `model_or_finetune_id` int NOT NULL,
--   `deploy_finetuned` tinyint(1) NOT NULL,
--   `start_time` datetime NOT NULL,
--   `end_time` datetime NOT NULL,
--   `name` varchar(100) NOT NULL,
--   `description` varchar(100) NOT NULL,
--   `port` int NOT NULL,
--   `params` json NOT NULL,
--   `devices` varchar(100) NOT NULL,
--   `state` int NOT NULL,
--   PRIMARY KEY (`entry_id`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -- END TABLE DEPLOYENTRIES

-- -- BEGIN TABLE DEPLOYACCESSCOUNTER
-- CREATE TABLE `DEPLOYACCESSCOUNTER` (
--   `id` int NOT NULL AUTO_INCREMENT,
--   `date` date NOT NULL,
--   `entry_id` int NOT NULL,
--   `count` int NOT NULL,
--   PRIMARY KEY (`id`),
--   KEY `DEPLOYACCESSCOUNT_TO_DEPLOYENTRIES` (`entry_id`),
--   CONSTRAINT `DEPLOYACCESSCOUNT_TO_DEPLOYENTRIES` FOREIGN KEY (`entry_id`) REFERENCES `DEPLOYENTRIES` (`entry_id`) ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -- END TABLE DEPLOYACCESSCOUNTER

-- -- BEGIN TABLE FINETUNEENTRIES
-- CREATE TABLE `FINETUNEENTRIES` (
--   `id` int NOT NULL AUTO_INCREMENT,
--   `name` varchar(255) NOT NULL,
--   `description` varchar(255) NOT NULL,
--   `model_id` varchar(255) NOT NULL,
--   `dataset_id` varchar(255) NOT NULL,
--   `devices` text NOT NULL,
--   `eval_indexes` text NOT NULL,
--   `output_dir` varchar(255) NOT NULL,
--   `adapter_name` varchar(255) NOT NULL,
--   `batch_size` int NOT NULL,
--   `micro_batch_size` int NOT NULL,
--   `num_epochs` int NOT NULL,
--   `learning_rate` float NOT NULL,
--   `cutoff_len` int NOT NULL,
--   `val_set_size` int NOT NULL,
--   `use_gradient_checkpointing` tinyint(1) NOT NULL,
--   `eval_step` int NOT NULL,
--   `save_step` int NOT NULL,
--   `logging_step` int NOT NULL,
--   `lora_r` float NOT NULL,
--   `lora_alpha` float NOT NULL,
--   `lora_dropout` float NOT NULL,
--   `num_virtual_tokens` int NOT NULL,
--   `train_on_inputs` tinyint(1) NOT NULL,
--   `group_by_length` tinyint(1) NOT NULL,
--   `bits_and_bytes` tinyint(1) NOT NULL,
--   `load_8bit` tinyint(1) NOT NULL,
--   `load_4bit` tinyint(1) NOT NULL,
--   `llm_int8_threshold` float NOT NULL,
--   `llm_int8_enable_fp32_cpu_offload` tinyint(1) NOT NULL,
--   `llm_int8_has_fp16_weight` tinyint(1) NOT NULL,
--   `bnb_4bit_compute_dtype` varchar(255) NOT NULL,
--   `bnb_4bit_quant_type` varchar(255) NOT NULL,
--   `bnb_4bit_use_double_quant` tinyint(1) NOT NULL,
--   `state` tinyint NOT NULL,
--   `start_time` datetime NOT NULL,
--   `end_time` datetime DEFAULT NULL,
--   PRIMARY KEY (`id`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -- END TABLE FINETUNEENTRIES

-- -- BEGIN TABLE EVALINDEXRECORDS
-- CREATE TABLE `EVALINDEXRECORDS` (
--   `id` int NOT NULL AUTO_INCREMENT,
--   `entry_id` int NOT NULL,
--   `name` varchar(255) NOT NULL,
--   `epoch` float NOT NULL,
--   `value` float NOT NULL,
--   PRIMARY KEY (`id`),
--   KEY `RATINGINDEXES_TO_FINETUNEENTRIES` (`entry_id`),
--   CONSTRAINT `RATINGINDEXRECORDS_TO_FINETUNEENTRIES` FOREIGN KEY (`entry_id`) REFERENCES `FINETUNEENTRIES` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -- END TABLE EVALINDEXRECORDS

-- -- BEGIN TABLE EVALRECORDS
-- CREATE TABLE `EVALRECORDS` (
--   `id` int NOT NULL AUTO_INCREMENT,
--   `loss` float NOT NULL,
--   `epoch` float NOT NULL,
--   `entry_id` int NOT NULL,
--   PRIMARY KEY (`id`),
--   KEY `LOGGINGRECORDS_TO_TINETUNEENTRIES` (`entry_id`),
--   CONSTRAINT `EVALRECORDS_TO_TINETUNEENTRIES` FOREIGN KEY (`entry_id`) REFERENCES `FINETUNEENTRIES` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -- END TABLE EVALRECORDS

-- -- BEGIN TABLE FINETUNEDATASETS
-- CREATE TABLE `FINETUNEDATASETS` (
--   `id` int NOT NULL AUTO_INCREMENT,
--   `entry_id` int NOT NULL,
--   `content` json NOT NULL,
--   PRIMARY KEY (`id`),
--   KEY `FINETUNEDATASETS_TO_DATASETENTRIES` (`entry_id`),
--   CONSTRAINT `FINETUNEDATASETS_TO_DATASETENTRIES` FOREIGN KEY (`entry_id`) REFERENCES `DATASETENTRIES` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -- END TABLE FINETUNEDATASETS

-- -- BEGIN TABLE FINETUNEPROGRESSES
-- CREATE TABLE `FINETUNEPROGRESSES` (
--   `id` int NOT NULL,
--   `current` int NOT NULL,
--   `total` int NOT NULL,
--   PRIMARY KEY (`id`),
--   CONSTRAINT `FINETUNEPROGRESSES_TO_FINETUNEENTRIES` FOREIGN KEY (`id`) REFERENCES `FINETUNEENTRIES` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -- END TABLE FINETUNEPROGRESSES

-- -- BEGIN TABLE LOGGINGRECORDS
-- CREATE TABLE `LOGGINGRECORDS` (
--   `id` int NOT NULL AUTO_INCREMENT,
--   `loss` float NOT NULL,
--   `learning_rate` float NOT NULL,
--   `epoch` float NOT NULL,
--   `step` int NOT NULL,
--   `entry_id` int NOT NULL,
--   PRIMARY KEY (`id`),
--   KEY `LOGGINGRECORDS_TO_TINETUNEENTRIES` (`entry_id`),
--   CONSTRAINT `LOGGINGRECORDS_TO_TINETUNEENTRIES` FOREIGN KEY (`entry_id`) REFERENCES `FINETUNEENTRIES` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -- END TABLE LOGGINGRECORDS

-- -- BEGIN TABLE OPENLLMS
-- CREATE TABLE `OPENLLMS` (
--   `model_id` int unsigned NOT NULL AUTO_INCREMENT,
--   `model_name` varchar(100) NOT NULL,
--   `model_description` varchar(100) NOT NULL,
--   `view_pic` varchar(100) NOT NULL,
--   `remote_path` varchar(100) NOT NULL,
--   `local_path` varchar(100) DEFAULT NULL,
--   `local_store` tinyint(1) NOT NULL,
--   `lora_support` tinyint(1) NOT NULL,
--   `lora_multi_device` tinyint(1) NOT NULL,
--   `prefix_tuning_support` tinyint(1) NOT NULL,
--   `prefix_tuning_multi_device` tinyint(1) NOT NULL,
--   `ptuning_support` tinyint(1) NOT NULL,
--   `ptuning_multi_device` tinyint(1) NOT NULL,
--   `prompt_tuning_support` tinyint(1) NOT NULL,
--   `prompt_tuning_multi_device` tinyint(1) NOT NULL,
--   `IA3_support` tinyint(1) NOT NULL,
--   `IA3_multi_device` tinyint(1) NOT NULL,
--   `storage_state` varchar(100) DEFAULT NULL,
--   `storage_date` date DEFAULT NULL,
--   `finetune` tinyint(1) NOT NULL,
--   `deployment` tinyint(1) NOT NULL,
--   PRIMARY KEY (`model_id`)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -- END TABLE OPENLLMS

-- -- BEGIN TABLE SIGNALS
-- CREATE TABLE `SIGNALS` (
--   `id` int NOT NULL AUTO_INCREMENT,
--   `signal` int NOT NULL,
--   `entry_id` int NOT NULL,
--   PRIMARY KEY (`id`),
--   KEY `SIGNALS_TO_FINETUNEENTRIES` (`entry_id`),
--   CONSTRAINT `SIGNALS_TO_FINETUNEENTRIES` FOREIGN KEY (`entry_id`) REFERENCES `FINETUNEENTRIES` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -- END TABLE SIGNALS


-- above are mysql version
-- migrate to postgresql version
-- use boolean instead of tinyint(1), and text instead of varchar(100)

-- BEGIN TABLE POOLS
CREATE TABLE POOLS (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  creation_date DATE NOT NULL,
  size INT NOT NULL,
  description TEXT NOT NULL
);

-- END TABLE POOLS

-- BEGIN TABLE DATASETENTRIES
CREATE TABLE DATASETENTRIES (
  id SERIAL PRIMARY KEY,
  pool_id INT NOT NULL,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  type INT NOT NULL,
  creation_date DATE NOT NULL,
  size INT NOT NULL,
  FOREIGN KEY (pool_id) REFERENCES POOLS(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE DATASETENTRIES

-- BEGIN TABLE DEPLOYENTRIES
CREATE TABLE DEPLOYENTRIES (
  entry_id SERIAL PRIMARY KEY,
  model_or_finetune_id INT NOT NULL,
  deploy_finetuned BOOLEAN NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  port INT NOT NULL,
  params JSON NOT NULL,
  devices TEXT NOT NULL,
  state INT NOT NULL
);

-- END TABLE DEPLOYENTRIES

-- BEGIN TABLE DEPLOYACCESSCOUNTER
CREATE TABLE DEPLOYACCESSCOUNTER (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  entry_id INT NOT NULL,
  count INT NOT NULL,
  FOREIGN KEY (entry_id) REFERENCES DEPLOYENTRIES(entry_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE DEPLOYACCESSCOUNTER

-- BEGIN TABLE FINETUNEENTRIES

CREATE TABLE FINETUNEENTRIES (
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
  lora_r FLOAT NOT NULL,
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
  state BOOLEAN NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP
);

-- END TABLE FINETUNEENTRIES

-- BEGIN TABLE EVALINDEXRECORDS
CREATE TABLE EVALINDEXRECORDS (
  id SERIAL PRIMARY KEY,
  entry_id INT NOT NULL,
  name TEXT NOT NULL,
  epoch FLOAT NOT NULL,
  value FLOAT NOT NULL,
  FOREIGN KEY (entry_id) REFERENCES FINETUNEENTRIES(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE EVALINDEXRECORDS

-- BEGIN TABLE EVALRECORDS
CREATE TABLE EVALRECORDS (
  id SERIAL PRIMARY KEY,
  loss FLOAT NOT NULL,
  epoch FLOAT NOT NULL,
  entry_id INT NOT NULL,
  FOREIGN KEY (entry_id) REFERENCES FINETUNEENTRIES(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE EVALRECORDS

-- BEGIN TABLE FINETUNEDATASETS
CREATE TABLE FINETUNEDATASETS (
  id SERIAL PRIMARY KEY,
  entry_id INT NOT NULL,
  content JSON NOT NULL,
  FOREIGN KEY (entry_id) REFERENCES DATASETENTRIES(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE FINETUNEDATASETS

-- BEGIN TABLE FINETUNEPROGRESSES
CREATE TABLE FINETUNEPROGRESSES (
  id INT NOT NULL,
  current INT NOT NULL,
  total INT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES FINETUNEENTRIES(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE FINETUNEPROGRESSES

-- BEGIN TABLE LOGGINGRECORDS
CREATE TABLE LOGGINGRECORDS (
  id SERIAL PRIMARY KEY,
  loss FLOAT NOT NULL,
  learning_rate FLOAT NOT NULL,
  epoch FLOAT NOT NULL,
  step INT NOT NULL,
  entry_id INT NOT NULL,
  FOREIGN KEY (entry_id) REFERENCES FINETUNEENTRIES(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE LOGGINGRECORDS

-- BEGIN TABLE OPENLLMS
CREATE TABLE OPENLLMS (
  model_id SERIAL PRIMARY KEY,
  model_name TEXT NOT NULL,
  model_description TEXT NOT NULL,
  view_pic TEXT NOT NULL,
  remote_path TEXT NOT NULL,
  local_path TEXT,
  local_store BOOLEAN NOT NULL,
  lora_support BOOLEAN NOT NULL,
  lora_multi_device BOOLEAN NOT NULL,
  prefix_tuning_support BOOLEAN NOT NULL,
  prefix_tuning_multi_device BOOLEAN NOT NULL,
  ptuning_support BOOLEAN NOT NULL,
  ptuning_multi_device BOOLEAN NOT NULL,
  prompt_tuning_support BOOLEAN NOT NULL,
  prompt_tuning_multi_device BOOLEAN NOT NULL,
  IA3_support BOOLEAN NOT NULL,
  IA3_multi_device BOOLEAN NOT NULL,
  storage_state TEXT,
  storage_date DATE,
  finetune BOOLEAN NOT NULL,
  deployment BOOLEAN NOT NULL
);

-- END TABLE OPENLLMS

-- BEGIN TABLE SIGNALS
CREATE TABLE SIGNALS (
  id SERIAL PRIMARY KEY,
  signal INT NOT NULL,
  entry_id INT NOT NULL,
  FOREIGN KEY (entry_id) REFERENCES FINETUNEENTRIES(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE SIGNALS