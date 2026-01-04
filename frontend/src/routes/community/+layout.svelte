<script>
    import Sidebar from './Sidebar.svelte';
  
    const sections = [
      { id: 'ai_chat', name: 'AI对话' },
      { id: 'infer_point', name: '在线推理' },
      { id: 'model_repo', name: '模型广场' },
      { id: 'owner_repo', name: '个人模型' },
      { id: 'create_task', name: '批量推理' },
      { id: 'ab_test_combined', name: 'A/B测试' },
      { id: 'index_article', name: '知识论坛' },
      { id: 'prompt_lab', name: 'Prompt实验室' },
      { id: 'eval', name: '模型评估' },
      { id: 'ide', name: '在线IDE' },
      { id: 'dify', name: '知识库' },
      { id: 'api_key', name: 'API Key管理' }
    ];
</script>

<Sidebar {sections} />
<div>
  <slot />
</div>