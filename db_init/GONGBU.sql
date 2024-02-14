-- BEGIN TABLE POOLS
CREATE TABLE "POOLS" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar(100) NOT NULL,
  "creation_date" date NOT NULL,
  "size" int NOT NULL,
  "description" varchar(100) NOT NULL
);

-- END TABLE POOLS

-- BEGIN TABLE DATASETENTRIES
CREATE TABLE "DATASETENTRIES" (
  "id" SERIAL PRIMARY KEY,
  "pool_id" int NOT NULL,
  "name" varchar(100) NOT NULL,
  "description" varchar(100) NOT NULL,
  "type" int NOT NULL,
  "creation_date" date NOT NULL,
  "size" int NOT NULL,
  FOREIGN KEY ("pool_id") REFERENCES "POOLS" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE DATASETENTRIES

-- BEGIN TABLE DEPLOYENTRIES
CREATE TABLE "DEPLOYENTRIES" (
  "entry_id" SERIAL PRIMARY KEY,
  "model_or_finetune_id" int NOT NULL,
  "deploy_finetuned" smallint NOT NULL,
  "start_time" timestamp without time zone NOT NULL,
  "end_time" timestamp without time zone NOT NULL,
  "name" varchar(100) NOT NULL,
  "description" varchar(100) NOT NULL,
  "port" int NOT NULL,
  "params" jsonb NOT NULL,
  "devices" varchar(100) NOT NULL,
  "state" int NOT NULL
);

-- END TABLE DEPLOYENTRIES

-- BEGIN TABLE DEPLOYACCESSCOUNTER
CREATE TABLE "DEPLOYACCESSCOUNTER" (
  "id" SERIAL PRIMARY KEY,
  "date" date NOT NULL,
  "entry_id" int NOT NULL,
  "count" int NOT NULL,
  FOREIGN KEY ("entry_id") REFERENCES "DEPLOYENTRIES" ("entry_id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE DEPLOYACCESSCOUNTER

-- BEGIN TABLE FINETUNEENTRIES
CREATE TABLE "FINETUNEENTRIES" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar(255) NOT NULL,
  "description" varchar(255) NOT NULL,
  "model_id" varchar(255) NOT NULL,
  "dataset_id" varchar(255) NOT NULL,
  "devices" text NOT NULL,
  "eval_indexes" text NOT NULL,
  "output_dir" varchar(255) NOT NULL,
  "adapter_name" varchar(255) NOT NULL,
  "batch_size" int NOT NULL,
  "micro_batch_size" int NOT NULL,
  "num_epochs" int NOT NULL,
  "learning_rate" real NOT NULL,
  "cutoff_len" int NOT NULL,
  "val_set_size" int NOT NULL,
  "use_gradient_checkpointing" smallint NOT NULL,
  "eval_step" int NOT NULL,
  "save_step" int NOT NULL,
  "logging_step" int NOT NULL,
  "lora_r" real NOT NULL,
  "lora_alpha" real NOT NULL,
  "lora_dropout" real NOT NULL,
  "num_virtual_tokens" int NOT NULL,
  "train_on_inputs" smallint NOT NULL,
  "group_by_length" smallint NOT NULL,
  "bits_and_bytes" smallint NOT NULL,
  "load_8bit" smallint NOT NULL,
  "load_4bit" smallint NOT NULL,
  "llm_int8_threshold" real NOT NULL,
  "llm_int8_enable_fp32_cpu_offload" smallint NOT NULL,
  "llm_int8_has_fp16_weight" smallint NOT NULL,
  "bnb_4bit_compute_dtype" varchar(255) NOT NULL,
  "bnb_4bit_quant_type" varchar(255) NOT NULL,
  "bnb_4bit_use_double_quant" smallint NOT NULL,
  "state" smallint NOT NULL,
  "start_time" timestamp without time zone NOT NULL,
  "end_time" timestamp without time zone DEFAULT NULL
);

-- END TABLE FINETUNEENTRIES

-- BEGIN TABLE EVALINDEXRECORDS
CREATE TABLE "EVALINDEXRECORDS" (
  "id" SERIAL PRIMARY KEY,
  "entry_id" int NOT NULL,
  "name" varchar(255) NOT NULL,
  "epoch" real NOT NULL,
  "value" real NOT NULL,
  FOREIGN KEY ("entry_id") REFERENCES "FINETUNEENTRIES" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE EVALINDEXRECORDS

-- BEGIN TABLE EVALRECORDS
CREATE TABLE "EVALRECORDS" (
  "id" SERIAL PRIMARY KEY,
  "loss" real NOT NULL,
  "epoch" real NOT NULL,
  "entry_id" int NOT NULL,
  FOREIGN KEY ("entry_id") REFERENCES "FINETUNEENTRIES" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE EVALRECORDS

-- BEGIN TABLE FINETUNEDATASETS
CREATE TABLE "FINETUNEDATASETS" (
  "id" SERIAL PRIMARY KEY,
  "entry_id" int NOT NULL,
  "content" jsonb NOT NULL,
  FOREIGN KEY ("entry_id") REFERENCES "DATASETENTRIES" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE FINETUNEDATASETS

-- BEGIN TABLE FINETUNEPROGRESSES
CREATE TABLE "FINETUNEPROGRESSES" (
  "id" int PRIMARY KEY,
  "current" int NOT NULL,
  "total" int NOT NULL,
  FOREIGN KEY ("id") REFERENCES "FINETUNEENTRIES" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE FINETUNEPROGRESSES

-- BEGIN TABLE LOGGINGRECORDS
CREATE TABLE "LOGGINGRECORDS" (
  "id" SERIAL PRIMARY KEY,
  "loss" real NOT NULL,
  "learning_rate" real NOT NULL,
  "epoch" real NOT NULL,
  "step" int NOT NULL,
  "entry_id" int NOT NULL,
  FOREIGN KEY ("entry_id") REFERENCES "FINETUNEENTRIES" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE LOGGINGRECORDS

-- BEGIN TABLE OPENLLMS
CREATE TABLE "OPENLLMS" (
  "model_id" SERIAL PRIMARY KEY,
  "model_name" varchar(100) NOT NULL,
  "model_description" varchar(100) NOT NULL,
  "view_pic" varchar(100) NOT NULL,
  "remote_path" varchar(100) NOT NULL,
  "local_path" varchar(100) DEFAULT NULL,
  "local_store" smallint NOT NULL,
  "lora_support" smallint NOT NULL,
  "lora_multi_device" smallint NOT NULL,
  "prefix_tuning_support" smallint NOT NULL,
  "prefix_tuning_multi_device" smallint NOT NULL,
  "ptuning_support" smallint NOT NULL,
  "ptuning_multi_device" smallint NOT NULL,
  "prompt_tuning_support" smallint NOT NULL,
  "prompt_tuning_multi_device" smallint NOT NULL,
  "IA3_support" smallint NOT NULL,
  "IA3_multi_device" smallint NOT NULL,
  "storage_state" varchar(100) DEFAULT NULL,
  "storage_date" date DEFAULT NULL,
  "finetune" smallint NOT NULL,
  "deployment" smallint NOT NULL
);

-- END TABLE OPENLLMS

-- BEGIN TABLE SIGNALS
CREATE TABLE "SIGNALS" (
  "id" SERIAL PRIMARY KEY,
  "signal" int NOT NULL,
  "entry_id" int NOT NULL,
  FOREIGN KEY ("entry_id") REFERENCES "FINETUNEENTRIES" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- END TABLE SIGNALS