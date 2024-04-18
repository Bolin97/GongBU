import NumberBoxParam from "./NumberBoxParam.svelte";
import SliderParam from "./SliderParam.svelte";
import BoolParam from "./BoolParam.svelte";
import SelectParam from "./SelectParam.svelte";
import RadioParam from "./RadioParam.svelte";
import MultiSelection from "./MultiSelection.svelte";

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
    name: "lora的秩",
    param_type: ParamType.number_box,
    description: "lora方法超参数",
    constrains: [{ min: 0 }, { values: [4, 8, 16, 32] }],
  },
  {
    var_name: "lora_alpha",
    name: "lora对模型效果的贡献度",
    param_type: ParamType.slider,
    description: "lora方法超参数",
    constrains: [{ min: 0 }, { max: 128 }],
  },
  {
    var_name: "lora_dropout",
    name: "dropout",
    param_type: ParamType.slider,
    description: "dropout",
    constrains: [{ max: 1.0 }, { step: 0.001 }],
  },
];

export const lora_quantization_params: Array<ParamEntry> = [
  {
    var_name: "load_xbit",
    name: "量化bit",
    param_type: ParamType.radio,
    description: "量化的参数",
    constrains: [{ values: [4, 8] }],
  },
];

export const lora_quantization_advanced: Array<ParamEntry> = [
  {
    var_name: "llm_int8_threshold",
    name: "llm_int8阈值",
    param_type: ParamType.slider,
    description: "高级量化参数",
    constrains: [{ min: 0.0 }, { max: 10.0 }],
  },
  {
    var_name: "llm_int8_enable_fp32_cpu_offload",
    name: "允许使用CPU进行fp32的卸载",
    param_type: ParamType.bool,
    description: "高级量化参数",
    constrains: [],
  },
  {
    var_name: "llm_int8_has_fp16_weight",
    name: "使用fp16旬行LLM.int8()",
    param_type: ParamType.bool,
    description: "高级量化参数",
    constrains: [],
  },
  {
    var_name: "bnb_4bit_compute_dtype",
    name: "设置计算类型",
    param_type: ParamType.select,
    description: "高级量化参数",
    constrains: [{ values: ["None", "fp4", "nf4"] }],
  },
  {
    var_name: "bnb_4bit_quant_type",
    name: "设置量化类型",
    param_type: ParamType.select,
    description: "高级量化参数",
    constrains: [{ values: ["fp4", "nf4"] }],
  },
  {
    var_name: "bnb_4bit_use_double_quant",
    name: "是否开启二次量化",
    param_type: ParamType.bool,
    description: "高级量化参数",
    constrains: [],
  },
];

export const num_virt_tokens_param: Array<ParamEntry> = [
  {
    var_name: "num_virtual_tokens",
    name: "虚拟token个数",
    description: "虚拟token个数",
    param_type: ParamType.slider,
    constrains: [{ min: 0 }, { max: 128 }],
  },
];

export const training_params: Array<ParamEntry> = [
  {
    var_name: "batch_size",
    name: "单次训练数据样本个数",
    param_type: ParamType.number_box,
    description: "训练超参数",
    constrains: [{ min: 0 }],
  },
  {
    var_name: "micro_batch_size",
    name: "每次流水并行的训练样本个数",
    param_type: ParamType.number_box,
    description: "训练超参数",
    constrains: [{ min: 0 }],
  },
  {
    var_name: "num_epochs",
    name: "训练迭代次数",
    param_type: ParamType.number_box,
    description: "训练超参数",
    constrains: [{ min: 0 }],
  },
  {
    var_name: "logging_step",
    name: "报告间隔",
    param_type: ParamType.number_box,
    description: "训练超参数",
    constrains: [{ min: 0 }],
  },
  {
    var_name: "cutoff_len",
    name: "文本最大长度",
    param_type: ParamType.number_box,
    description: "训练超参数",
    constrains: [{ min: 0 }],
  },
  {
    var_name: "eval_step",
    name: "评估步数间隔",
    param_type: ParamType.number_box,
    description: "高级训练参数",
    constrains: [{ min: 0 }],
  },
  {
    var_name: "val_set_size",
    name: "评估数据集的大小",
    param_type: ParamType.slider,
    description: "训练超参数",
    constrains: [{ min: 0 }, { max: 1 }, { step: 0.001 }],
  },
  {
    var_name: "use_gradient_checkpointing",
    name: "是否使用梯度检查点",
    param_type: ParamType.bool,
    description: "高级训练参数",
    constrains: [],
  },
  {
    var_name: "zero_optimization",
    name: "是否使用zero优化",
    param_type: ParamType.bool,
    description: "高级训练参数",
    constrains: [],
  },
  {
    var_name: "zero_stage",
    name: "zero优化阶段",
    param_type: ParamType.radio,
    description: "高级训练参数",
    constrains: [{ values: [1, 2, 3] }],
  },
  {
    var_name: "zero_offload",
    name: "是否使用zero卸载",
    param_type: ParamType.bool,
    description: "高级训练参数",
    constrains: [],
  },
];

export const training_advanced: Array<ParamEntry> = [
  {
    var_name: "learning_rate",
    name: "学习率",
    param_type: ParamType.slider,
    description: "训练超参数",
    constrains: [{ min: 0.0 }, { max: 0.01 }, { step: 0.00001 }],
  },
  {
    var_name: "save_step",
    name: "保存步数间隔",
    param_type: ParamType.number_box,
    description: "高级训练参数",
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
// export interface DeploymentRequestParams {
//     "model_or_adpater_id": number,
//     "deploy_base_model": boolean,
//     "bits_and_bytes": true,
//     "load_8bit": true,
//     "load_4bit": true,
//     "use_flash_attention": true,
//     "use_deepspeed": true,
//     "devices": [
//       "string"
//     ],
//     "port": 0
// }

export const deployment_params: Array<ParamEntry> = [
  {
    var_name: "bits_and_bytes",
    name: "是否使用bits_and_bytes",
    param_type: ParamType.bool,
    description: "部署参数",
    constrains: [],
  },
  {
    var_name: "use_flash_attention",
    name: "是否使用flash attention",
    param_type: ParamType.bool,
    description: "部署参数",
    constrains: [],
  },
  {
    var_name: "use_deepspeed",
    name: "是否使用deepspeed",
    param_type: ParamType.bool,
    description: "部署参数",
    constrains: [],
  },
];

export const deployment_port: Array<ParamEntry> = [
  {
    var_name: "port",
    name: "端口",
    param_type: ParamType.number_box,
    description: "部署参数",
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
    name: "量化bit",
    param_type: ParamType.radio,
    description: "部署参数",
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
  };
}
