import NumberBoxParam from "./NumberBoxParam.svelte";
import SliderParam from "./SliderParam.svelte";
import BoolParam from "./BoolParam.svelte";
import SelectParam from "./SelectParam.svelte";
import RadioParam from "./RadioParam.svelte";
import MultiSelection from "./MultiSelection.svelte";
// import { getContext } from "svelte";
// const t: any = getContext("t");
import { t } from "../../../locales";

export interface Constrain {}

export interface ChooseFromConstrain extends Constrain {
  values: Array<string | number>;
}

export interface MaxValueConstrain extends Constrain {
  max: number;
}

export interface MinValueConstrain extends Constrain {
  min: number;
}

export interface StepConstrain extends Constrain {
  step: number;
}

export enum ParamType {
  number_box = 0,
  slider = 1,
  bool = 2,
  select = 3,
  radio = 4,
  multi_select = 5,
}

export const param_component_mapper = [
  NumberBoxParam,
  SliderParam,
  BoolParam,
  SelectParam,
  RadioParam,
  MultiSelection,
];

export interface ParamEntry {
  param_type: ParamType;
  constrains: Array<Constrain>;
  name: string;
  var_name: string;
  description: string;
}

export function parse_cons(cons: Array<Constrain>) {
  const max_cons = cons.filter((item) => {
    return "max" in item;
  });
  const min_cons = cons.filter((item) => {
    return "min" in item;
  });
  const step_cons = cons.filter((item) => {
    return "step" in item;
  });
  const choose_from_cons = cons.filter((item) => {
    return "values" in item;
  });
  return {
    max:
      max_cons.length == 0
        ? 1048576
        : (max_cons.pop() as MaxValueConstrain).max,
    min: min_cons.length == 0 ? 0 : (min_cons.pop() as MinValueConstrain).min,
    step: step_cons.length == 0 ? 1 : (step_cons.pop() as StepConstrain).step,
    values:
      choose_from_cons.length == 0
        ? []
        : (choose_from_cons.pop() as ChooseFromConstrain).values,
  };
}

export const lora_specific_params: Array<ParamEntry> = [
  {
    var_name: "lora_r",
    name: t("finetune.finetune_params.lora_params.lora_r"),
    param_type: ParamType.number_box,
    description: t("finetune.finetune_params.lora_params.lora_r_des"),
    constrains: [{ min: 0 }, { values: [4, 8, 16, 32] }],
  },
  {
    var_name: "lora_alpha",
    name: t("finetune.finetune_params.lora_params.lora_alpha"),
    param_type: ParamType.slider,
    description: t("finetune.finetune_params.lora_params.lora_alpha_des"),
    constrains: [{ min: 0 }, { max: 128 }],
  },
  {
    var_name: "lora_dropout",
    name: t("finetune.finetune_params.lora_params.lora_dropout"),
    param_type: ParamType.slider,
    description: t("finetune.finetune_params.lora_params.lora_dropout_des"),
    constrains: [{ max: 1.0 }, { step: 0.001 }],
  },
];

export const lora_quantization_params: Array<ParamEntry> = [
  {
    var_name: "load_xbit",
    name: t("finetune.finetune_params.qlora_params.bit"),
    param_type: ParamType.radio,
    description: t("finetune.finetune_params.qlora_params.bit_des"),
    constrains: [{ values: [4, 8] }],
  },
];

export const lora_quantization_advanced: Array<ParamEntry> = [
  {
    var_name: "llm_int8_threshold",
    name: t("finetune.finetune_params.qlora_params.q_int8"),
    param_type: ParamType.slider,
    description: t("finetune.finetune_params.qlora_params.q_int8_des"),
    constrains: [{ min: 0.0 }, { max: 10.0 }],
  },
  {
    var_name: "llm_int8_enable_fp32_cpu_offload",
    name: t("finetune.finetune_params.qlora_params.q_cpu_offload"),
    param_type: ParamType.bool,
    description: t("finetune.finetune_params.qlora_params.q_cpu_offload_des"),
    constrains: [],
  },
  {
    var_name: "llm_int8_has_fp16_weight",
    name: t("finetune.finetune_params.qlora_params.q_fp16_int8"),
    param_type: ParamType.bool,
    description: t("finetune.finetune_params.qlora_params.q_fp16_int_des"),
    constrains: [],
  },
  {
    var_name: "bnb_4bit_compute_dtype",
    name: t("finetune.finetune_params.qlora_params.q_compute_type"),
    param_type: ParamType.select,
    description: t("finetune.finetune_params.qlora_params.q_compute_type_des"),
    constrains: [{ values: ["None", "fp4", "nf4"] }],
  },
  {
    var_name: "bnb_4bit_quant_type",
    name: t("finetune.finetune_params.qlora_params.q_type"),
    param_type: ParamType.select,
    description: t("finetune.finetune_params.qlora_params.q_type_des"),
    constrains: [{ values: ["fp4", "nf4"] }],
  },
  {
    var_name: "bnb_4bit_use_double_quant",
    name: t("finetune.finetune_params.qlora_params.q_quad"),
    param_type: ParamType.bool,
    description: t("finetune.finetune_params.qlora_params.q_quad_des"),
    constrains: [],
  },
];

export const num_virt_tokens_param: Array<ParamEntry> = [
  {
    var_name: "num_virtual_tokens",
    name: t("finetune.finetune_params.p_params.tokens_number"),
    description: t("finetune.finetune_params.qlora_params.tokens_number_des"),
    param_type: ParamType.slider,
    constrains: [{ min: 0 }, { max: 128 }],
  },
];

export const training_params: Array<ParamEntry> = [
  {
    var_name: "batch_size",
    name: t("finetune.finetune_params.train_params.batch_size"),
    param_type: ParamType.number_box,
    description: t("finetune.finetune_params.train_params.batch_size_des"),
    constrains: [{ min: 0 }],
  },
  {
    var_name: "micro_batch_size",
    name: t("finetune.finetune_params.train_params.micro_batch_size"),
    param_type: ParamType.number_box,
    description: t("finetune.finetune_params.train_params.micro_batch_size_des"),
    constrains: [{ min: 0 }],
  },
  {
    var_name: "num_epochs",
    name: t("finetune.finetune_params.train_params.epochs"),
    param_type: ParamType.number_box,
    description: t("finetune.finetune_params.train_params.epochs_des"),
    constrains: [{ min: 0 }],
  },
  {
    var_name: "logging_step",
    name: t("finetune.finetune_params.train_params.log_steps"),
    param_type: ParamType.number_box,
    description: t("finetune.finetune_params.train_params.log_steps_des"),
    constrains: [{ min: 0 }],
  },
  {
    var_name: "cutoff_len",
    name: t("finetune.finetune_params.train_params.cut_off_len"),
    param_type: ParamType.number_box,
    description: t("finetune.finetune_params.train_params.cut_off_len_des"),
    constrains: [{ min: 0 }],
  },
  {
    var_name: "eval_step",
    name: t("finetune.finetune_params.train_params.eval_steps"),
    param_type: ParamType.number_box,
    description: t("finetune.finetune_params.train_params.eval_steps_des"),
    constrains: [{ min: 0 }],
  },
  {
    var_name: "val_set_size",
    name: t("finetune.finetune_params.train_params.eval_data_size"),
    param_type: ParamType.slider,
    description: t("finetune.finetune_params.train_params.eval_data_size"),
    constrains: [{ min: 0 }, { max: 1 }, { step: 0.001 }],
  },
  {
    var_name: "use_gradient_checkpointing",
    name: t("finetune.finetune_params.train_params.checkpoint"),
    param_type: ParamType.bool,
    description: t("finetune.finetune_params.train_params.checkpoint_des"),
    constrains: [],
  },
  {
    var_name: "zero_optimization",
    name: t("finetune.finetune_params.train_params.zero_opt"),
    param_type: ParamType.bool,
    description: t("finetune.finetune_params.train_params.zero_opt_des"),
    constrains: [],
  },
  {
    var_name: "zero_stage",
    name: t("finetune.finetune_params.train_params.zero_stage"),
    param_type: ParamType.radio,
    description: t("finetune.finetune_params.train_params.zero_stage_des"),
    constrains: [{ values: [1, 2, 3] }],
  },
  {
    var_name: "zero_offload",
    name: t("finetune.finetune_params.train_params.zero_offload"),
    param_type: ParamType.bool,
    description: t("finetune.finetune_params.train_params.zero_offload_des"),
    constrains: [],
  },
];

export const training_advanced: Array<ParamEntry> = [
  {
    var_name: "learning_rate",
    name: t("finetune.finetune_params.train_params.learn_rate"),
    param_type: ParamType.slider,
    description: t("finetune.finetune_params.train_params.learn_rate_des"),
    constrains: [{ min: 0.0 }, { max: 0.01 }, { step: 0.00001 }],
  },
  {
    var_name: "save_step",
    name: t("finetune.finetune_params.train_params.save_steps"),
    param_type: ParamType.number_box,
    description: t("finetune.finetune_params.train_params.save_steps_des"),
    constrains: [{ min: 0 }],
  },
];

export function default_finetune_params() {
  return {
    batch_size: 4,
    micro_batch_size: 1,
    num_epochs: 10,
    learning_rate: 0.0003,
    cutoff_len: 512,
    val_set_size: 0.3,
    use_gradient_checkpointing: true,
    eval_step: 1,
    save_step: 8,
    logging_step: 1,
    lora_r: 8,
    lora_alpha: 16,
    lora_dropout: 0.05,
    num_virtual_tokens: 30,
    load_xbit: 8,
    llm_int8_threshold: 6.0,
    llm_int8_enable_fp32_cpu_offload: false,
    llm_int8_has_fp16_weight: false,
    bnb_4bit_compute_dtype: "None",
    bnb_4bit_quant_type: "fp4",
    bnb_4bit_use_double_quant: false,
    zero_optimization: false,
    zero_stage: 2,
    zero_offload: false,
    use_dora: false,
    use_rslora: false,
    rank_dropout: 0.0,
    module_dropout: 0.0,
    use_effective_conv2d: false,
    use_flash_attention: false,
  };
}

export const deployment_params: Array<ParamEntry> = [
  // {
  //   var_name: "bits_and_bytes",
  //   name: t("components.deployment_params.bits_and_bytes"),
  //   param_type: ParamType.bool,
  //   description: t("components.deployment_params.description"),
  //   constrains: [],
  // },
  // {
  //   var_name: "use_flash_attention",
  //   name: t("components.deployment_params.use_flash_attention"),
  //   param_type: ParamType.bool,
  //   description: t("components.deployment_params.description"),
  //   constrains: [],
  // },
  // {
  //   var_name: "use_deepspeed",
  //   name: t("components.deployment_params.use_deepspeed"),
  //   param_type: ParamType.bool,
  //   description: t("components.deployment_params.description"),
  //   constrains: [],
  // },
  {
    var_name: "use_vllm",
    name: t("components.deployment_params.use_vllm"),
    param_type: ParamType.bool,
    description: t("components.deployment_params.description"),
    constrains: [],
  },
];

export const deployment_port: Array<ParamEntry> = [
  {
    var_name: "port",
    name: t("deployment.task.port"),
    param_type: ParamType.number_box,
    description: t("components.deployment_params.description"),
    constrains: [
      { min: 1000 },
      { max: 65535 },
      { values: [8760, 8761, 8762, 8763, 8764, 8765, 8766, 8767] },
    ],
  },
];

export const deployment_quantization_params: Array<ParamEntry> = [
  {
    var_name: "load_xbit",
    name: t("deployment.task.quan_bit"),
    param_type: ParamType.radio,
    description: t("components.deployment_params.description"),
    constrains: [{ values: [4, 8] }],
  },
];

export function default_deployment_params() {
  return {
    bits_and_bytes: false,
    load_xbit: 8,
    use_flash_attention: false,
    use_deepspeed: false,
    port: 8760,
    use_vllm: false,
  };
}
