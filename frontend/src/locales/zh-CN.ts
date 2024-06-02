export default {
  root: {
    login: "登陆",
    username: "用户名",
    password: "密码",
    title: "工部 大模型平台",
    login_failed: "登陆失败，请检查用户名和密码。",
    sign_up_token: "注册验证Token",
    sign_up: "注册",
    switch_to_login: "切换到登陆页",
    switch_to_signup: "切换到注册页",
    signup_failed: "注册失败，请检查注册验证Token。",
    signup_successful: "注册成功，请登陆。",
    sign_up_token_required: "注册验证Token是必需的。",
    password_not_match: "密码与确认密码不匹配。",
    password_confirm: "确认密码",
  },
  model: {
    deploy: "部署",
    finetune: "微调",
  },
  components: {
    model_card: {
      adapters: "Adapters",
      id: "ID",
      name_and_description: "名称 & 描述",
      action: "操作",
    },
    visibility_button: {
      hide: "隐藏",
      publicize: "公开",
    },
    go_back: "返回",
    data: {
      data_pool_selector: "数据池：",
      data_pool_des: "选择数据池",
      data_set_selector: "数据集：",
      data_set_des: "从所选的数据池中选择数据集"
    },
    eval_metrics_description: {
      acc_des: "预测正确的样本数/样本数总数",
      recall_des: "基于召回率判断两个句子的相似程度",
      f1score_des: "Accuracy和Recall的调和指标",
      pre_des: "评估生成文本中与参考文本匹配的内容所占的比例",
      bleu_des: "基于准确率判断两个句子的相似程度",
      distinct_des: "反映文本生成的多样性"
    },
    device: {
      GPU_utilization: "GPU利用率：",
      memory_utilization: "显存利用率：",
    },
    deployment_params: {
      title: "部署参数",
      subtitle: "量化参数",
      subsubtitle: "量化部署参数",
      bits_and_bytes: "是否使用bits_and_bytes",
      use_flash_attention: "是否使用flash attention",
      use_deepspeed: "是否使用deepspeed",
      use_vllm: "是否使用vllm",
      description: "部署参数"
    }
  },
  fault: {
    title: "错误记录",
    description: "查看任务和进程发生错误的日志",
    message: "错误信息",
    source: "来源",
    time: "时间",
    code: "错误码",
    action: "操作",
    view_logs: "查看日志",
    download_logs: "下载日志",
    search_placeholder: "输入标签，用半角逗号分隔",
    search: "搜索",
  },
  config: {
    log_out: "登出",
    model_list: "模型列表",
    title: "设置",
    description: "配置系统参数"
  },
  sidebar: {
    model_squre: "模型广场",
    finetune_manager: "微调管理",
    data_manager: "数据管理",
    model_eval: "模型评估",
    deployment_manager: "部署管理",
    model_download: "模型下载",
    error_log: "错误记录",
    settings: "设置",
  },
  model_square: {
    title: "模型广场",
    description: "集中展示与管理预置开源大模型，支持对模型进行微调与部署"
  },
  deployment: {
    title: "部署管理",

    description: "部署基模型或已微调模型",
    task: {
      button: "创建部署任务",
      title: "创建部署任务",
      des: "部署任务的创建与管理",
      task_name: "任务名称:",
      task_description: "任务描述:",
      enter_task_name: "在此输入任务名称",
      enter_task_description: "在此输入任务描述",
      next_step: "下一步",
      previous_step: "上一步",
      choose_at_least_one_device: "至少选择一个设备",
      complete: "完成",
      steps:{
        model: "模型选择",
        device: "设备选择",
        params: "参数选择",
        name: "任务名称",
        model_des: "选择合适的模型",
        device_des: "选择可支持微调的本地设备",
        params_des: "选择部署参数",
        name_des: "输入项目名称与描述"
      },
      port: "端口号：",
      quan_bit: "量化参数："
    },
    detail: {
      title: "详细信息",
      stop: "停止",
      start: "启动",
      state: "进度：",
      model: "模型：",
      gradio_link: "Gradio 链接：",
      adapter: "微调方法：",
      deepspeed: "是否使用Deepspeed：",
      flash_attention: "是否使用Flash Attention: ",
      device: "设备：",
      p1: "部署未开始",
      vllm: "是否使用VLLM：",
      delete: {
        title: "确认删除",
        p1: "确认要删除吗？",
        p2: "删除后，该任务的所有相关信息将",
        p3: "无法",
        p4: "恢复。",
        yes: "删除",
        no: "不"
      }
    },
    stopped: "已停止",
    starting: "启动中",
    running: "运行中",
    error: "出错",
  },
  eval: {
    title: "模型评估",
    subtitle: "评估基础模型或已训练模型的表现",
    create_task: "创建评估任务",
    next_step: "下一步",
    previous_step: "上一步",
    eval_size: "验证集大小",
    recommended_value: "推荐值",
    detail: {
      running: "进行中",
      title: "详细信息",
      state: "进度：",
      loading_model: "加载模型",
      starting: "开始中",
      generating: "生成中",
      evaluating: "评估中",
      done: "完成",
      adapter: "微调方法：",
      dataset_name: "数据集名称：",
      dataset_des: "数据集描述：",
      dataset_size: "数据集大小：",
      bits_and_bytes: "量化：",
      val_set_size: "评估集大小：",
      use_deepspeed: "使用deepspeed：",

      delete:{
        delete: "delete",
        title: "Confirm Deletion",
        p1: "Are you sure you want to delete?",
        p2: "After deletion, all related information of this task will be ",
        p3: "irrecoverable",

      }
    },
    task: {
      title: "评估任务",
      subtitle: "评估任务的创建与管理",
      next_step: "下一步",
      previous_step: "上一步",
      complete: "完成",
    },
    steps:{
      model_selection: "模型选择",
      data_selection: "数据选择",
      evaluation_metrics: "评估指标",
      params_selection: "参数选择",
      device_selection: "设备选择",
      project_name: "项目名称",
      choose_model: "选择合适的开源大模型",
      choose_data: "选择已上传到数据池的数据",
      choose_metrics: "选择评估指标",
      choose_params: "选择评估的可配置参数",
      choose_device: "选择运行评估的本地设备",
      input_name: "输入项目名称与描述",
    },
    input:{
      task_name: "任务名称",
      task_description: "任务描述",
      enter_task_name: "在此输入任务名称",
      enter_task_description: "在此输入任务描述",
    }
  },
  finetune: {
    model: "模型",
    training: "训练中",
    training_completed: "训练完成",
    error: "出错",
    invalid_status_code: "无效状态码",
    details: "微调详情",
    management: "微调管理",
    finetune: "创建和管理微调任务",
    create_task: "创建微调任务",
    model_selection: "模型选择",
    data_selection: "数据选择",
    evaluation_metrics: "评估指标",
    fine_tuning: "微调方法",
    device_selection: "设备选择",
    output_selection: "输出选择",
    project_name: "项目名称",
    choose_model: "选择合适的开源大模型",
    choose_data: "选择已上传到数据池的数据",
    choose_metrics: "选择评估指标",
    choose_tuning: "选择平台支持的微调方法并配置参数",
    choose_device: "选择可支持微调的本地设备",
    input_name: "输入项目名称与描述",
    task_name: "任务名称",
    task_description: "任务描述",
    enter_task_name: "在此输入任务名称",
    enter_task_description: "在此输入任务描述",
    next_step: "下一步",
    previous_step: "上一步",
    choose_at_least_one_device: "至少选择一个设备",
    complete: "完成",
    loading: "加载中",
    cancel: "取消",
    train_loss: "训练Loss",
    eval_loss: "评估Loss",
    finetune_params: {
      finetune_method_select: "微调方法选择：",
      lora_params: {
        title: "lora参数",
        lora_r: "lora方法的秩",
        lora_r_des: "分解成的低秩序矩阵的秩",
        lora_alpha: "lora权重对模型效果的贡献度",
        lora_alpha_des: "alpha越大，lora方法对模型输出的影响越大",
        lora_dropout: "lora方法的剪枝率",
        lora_dropout_des: "对一些lora权重进行剪枝的比例",
        recommended_value: "推荐值"
      },
      qlora_params: {
        title: "qlora量化参数",
        bit: "量化位数",
        bit_des: "对模型参数量化的bit数",
        advanced_options_title: "高级选项",
        q_params_ad: "lora量化参数（高级）",
        q_int8: "llm_int8阈值",
        q_int8_des: "在量化中，将模型的权重转换为int8，减少模型所需的显存",
        q_cpu_offload: "允许使用CPU进行fp32的卸载",
        q_cpu_offload_des: "使用cpu加载量化前的fp32参数，而非GPU，可以节省显存",
        q_fp16_int8: "是否使用fp16并行LLM.int8()",
        q_fp16_int8_des: "是否进行混合精度计算",
        q_compute_type: "设置计算类型",
        q_compute_type_des: "选择量化过程的计算类型",
        q_type: "设置量化类型",
        q_type_des: "选择量化的类型",
        q_quad: "是否开启二次量化",
        q_quad_des: "如显存仍然不足，可以尝试二次量化",
      },
      p_params: {
        title: "虚拟token参数",
        tokens_number: "虚拟token个数",
        tokens_number_des: "微调方法的前缀或prompt的长度"
      },
      train_params: {
        title: "训练参数",
        batch_size: "单词训练数据样本个数",
        micro_batch_size: "每次流水并行的训练样本个数",
        epochs: "训练迭代次数",
        log_steps: "报告间隔",
        save_steps: "保存步数间隔",
        eval_steps: "评估步数间隔",
        cut_off_len: "文本最大长度",
        eval_data_size: "评估数据集大小",
        checkpoint: "是否使用梯度检查点",
        zero_opt: "是否使用zero优化",
        zero_stage: "zero优化阶段",
        zero_offload: "是否使用zero卸载",
        learn_rate: "学习率",
        batch_size_des: "单词训练数据样本个数",
        micro_batch_size_des: "每次流水并行的训练样本个数",
        epochs_des: "训练迭代次数",
        log_steps_des: "报告间隔",
        save_steps_des: "保存步数间隔",
        eval_steps_des: "评估步数间隔",
        cut_off_len_des: "文本最大长度",
        eval_data_size_des: "评估数据集大小",
        checkpoint_des: "是否使用梯度检查点",
        zero_opt_des: "是否使用zero优化",
        zero_stage_des: "zero优化阶段",
        zero_offload_des: "是否使用zero卸载",
        learn_rate_des: "学习率",
        advanced_options_title: "高级选项",
        train_params_ad: "训练参数（高级）",
      }
    },
    device_params: {
      auto: "自动分配",
      local_devices: "本地设备"
    },
    detail:{
      yes: "是的",
      no: "不",
      title: "详细信息",
      real_time_data: "实时数据",
      deployment: "部署",
      method: "微调方法: ",
      device: "训练设备当前状态:",
      data: "数据集:",
      save_path: "保存路径:",
      advanced: "高级:",
      interrupt:{
        title: "确认打断",
        interrupt: "打断",
        p1: "确认要打断训练吗？",
        p2: "程序不会立即停止训练，而是将在输入打断信号后的第一个训练step后结束训练。",
        p3: "训练的进度和结果将",
        p4: "不会",
        p5: "被保存。"
      },
      delete:{
        title: "删除",
        delete: "确认删除",
        p1: "确认要删除吗？",
        p2: "删除后，该任务的所有相关信息将",
        p3: "无法",
        p4: "恢复。",
        p5: "我确认要",
        p6: "删除",
        p7: "该任务记录及其相关文件",
      }
    }
  },

  data:{
    title: "数据管理",
    description: "创建与管理数据池，上传数据集到数据池，支持对数据进行各种操作",
    create_pool: "创建数据池",
    no_dataset: "数据池中无数据集",
    detail: {
      title: "查看详情",
      detail: "数据池详情",
      delete: "删除此数据池",
      filter: "自动筛选",
      create_on: "创建时间：",
      size: "数据量：",
      title_1: "确认删除吗",
      p1: "确认要删除吗？",
      p2: "数据将",
      p3: "无法",
      p4: "恢复。",
      yes: "是的",
      no: "不",
      title_2: "暂存区中仍有未提交的数据",
      p5: "确认要返回吗？暂存区中仍有未提交的数据。",
      p6: "暂存区的数据将",
      p7: "不会",
      p8: "被保存。",
    },
    table:{
      col_name: "名称",
      col_time: "创建时间",
      col_size: "数据量",
      col_format: "格式",
      col_des: "描述"
    },
    delete: {
      title: "确认删除",
      data: "删除数据",
      p1: "确认要删除这个数据集吗？",
      p2: "删除后数据将不可恢复。",
      yes: "删除",
      no: "不"
    },
    uploader:{
      col_filename: "文件名",
      col_datasetname: "数据集名",
      col_des: "描述",
      col_option: "操作",
      datapool_detail: "数据池详细信息",
      zone: "暂存区",
      format: "格式",
      submit: "提交暂存区的所有文件",
      no_file: "暂存区内无已上传文件",
      enter_name: "输入数据集名称",
      enter_des: "输入数据集描述",
      move: "移出暂存区",
      click: "点击",
      or: "或",
      p1: "拖拽",
      p2: "以上传文件至暂存区"
    },
    task: {
      steps: {
        infor: "基本信息",
        upload: "上传数据",
        infor_des: "填写所创建数据池的基本信息",
        upload_des: "选择需要上传的数据"
      },
      p1: "确认已创建完成吗？暂存区中仍有未提交的数据。",
      p2: "暂存区的数据将",
      p3: "不会",
      p4: "被保存。",
      yes: "是的",
      no: "不",
      title: "创建数据池",
      description: "按照提示步骤创建数据池",
      complete: "完成",
      name: "数据池名称",
      enter_name: "请输入数据池名称",
      des: "数据池描述",
      enter_des: "请输入数据池描述"
    },
    filter:{
      title: "数据筛选",
      p1: "原始数据集：",
      p2: "保留比例：",
      name: "新数据集名称：",
      des: "新数据集描述：",
      begin: "开始筛选"
    }
  },

  download:{
    title: "模型下载",
    model: "已有模型",
    description: "通过编辑配置文件来下载大模型",
    alert: " 关闭所有提醒 ",
    list: "模型列表",
    list_alert: "模型列表无效，请重设。",
    p1: "信息已写入，模型文件已开始下载。",
    p2: "自动下载",
    p3: "下载得到的，包含config.json的文件夹重命名为",
    p4: "并放入models文件夹。",
    p5: "仅写入信息（手动下载）",
    delete: {
      title: "确认删除",
      p1: "确定要删除这个模型的所有记录和文件吗？",
      p2: "此操作",
      p3: "无法撤回",
      p4: "模型的文件将",
      p5: "不会",
      p6: "被删除。",
      p7: "删除记录和模型文件",
      p8: "仅删除记录",
      delete: "删除",
      no: "不",
    },
    table:{
      model: "模型",
      des: "描述",
      website: "下载地址",
      options: "操作",
      state: "操作"
    }
  }
  
};
