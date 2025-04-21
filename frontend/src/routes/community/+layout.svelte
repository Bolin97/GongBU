<script>
    import Sidebar from './Sidebar.svelte';
  
    const sections = [
      { id: 'ai-chat', name: 'AI对话' },
      { id: 'model_repo', name: '模型广场' },
      { id: 'my-models', name: '个人模型' },
      { id: 'articles', name: '文章分享平台' },
      { id: 'inference', name: '在线推理' },
      { id: 'ide', name: '在线IDE' },
      { id: 'api-keys', name: 'API Key管理' }
    ];
</script>

<Sidebar {sections} />