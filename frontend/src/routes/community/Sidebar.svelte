<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount, onDestroy } from 'svelte';

  // 定义类型
  interface Section {
    id: string;
    name: string;
    description?: string;
  }

  interface Category {
    id: string;
    name: string;
    icon: string;
    description: string;
    items: Section[];
  }

  export let sections: Section[] = [];
  export let activeSection: string = "";

  // 为每个部分添加描述
  const sectionDescriptions: Record<string, string> = {
    "ai_chat": "支持多模态交互与高并发流式响应",
    "infer_point": "在线推理服务，支持OpenAI兼容API",
    "create_task": "离线任务调度，接入在线推理服务",
    "model_repo": "支持从HuggingFace、GitHub导入远程模型",
    "owner_repo": "模型管理、Git版本控制、协作开发",
    "ab_test_combined": "多模型、多Prompt对比，支持差异高亮",
    "prompt_lab": "Prompt编写、测试、版本管理",
    "eval": "多任务支持：翻译、问答、摘要、分类等",
    "dify": "支持文本块检索、问答、私有文档嵌入",
    "ide": "项目目录管理、批量保存、Python在线运行",
    "api_key": "创建、权限控制、调用量统计、安全配置",
    "index_article": "文章推荐、评论系统、问答区"
  };

  // 为每个部分添加描述
  const enrichedSections = sections.map(section => ({
    ...section,
    description: sectionDescriptions[section.id] || ""
  }));

  // 将菜单项按模块分类
  let moduleCategories: Category[] = [
    {
      id: "ai_chat",
      name: "AI对话模块",
      icon: "💬",
      description: "支持多模态交互与高并发流式响应",
      items: []
    },
    {
      id: "inference",
      name: "推理模块",
      icon: "🧠",
      description: "提供统一的模型在线和离线推理接入点",
      items: []
    },
    {
      id: "model_management",
      name: "模型管理模块",
      icon: "📦",
      description: "构建完整模型生命周期管理系统",
      items: []
    },
    {
      id: "experiment",
      name: "实验与测试模块",
      icon: "🧪",
      description: "为Prompt工程和效果评估提供工具",
      items: []
    },
    {
      id: "evaluation",
      name: "评估与分析模块",
      icon: "📊",
      description: "建立面向多任务的评估框架",
      items: []
    },
    {
      id: "development",
      name: "开发支持模块",
      icon: "💻",
      description: "面向开发者提供端到端的开发体验",
      items: []
    },
    {
      id: "community",
      name: "社区模块",
      icon: "👥",
      description: "建立用户参与和知识传播的社区生态",
      items: []
    }
  ];

  // 获取每个模块的图标
  const getItemIcon = (id: string): string => {
    const iconMap: Record<string, string> = {
      "ai_chat": "🤖",
      "infer_point": "⚡",
      "create_task": "📋",
      "model_repo": "🏪",
      "owner_repo": "📁",
      "ab_test_combined": "🔍",
      "prompt_lab": "✏️",
      "eval": "📈",
      "dify": "🔎",
      "ide": "🖥️",
      "api_key": "🔑",
      "index_article": "📚"
    };
    return iconMap[id] || "📌";
  };

  // 处理点击事件
  const handleClick = (section: Section): void => {
    activeSection = section.id;
    fetchContent(section.id);
  };

  // 获取内容
  async function fetchContent(sectionId: string): Promise<void> {
    // 在导航前恢复滚动功能，确保其他页面可以正常滚动
    document.body.style.overflow = originalBodyOverflow;

    if (sectionId != "dify") {
      const url = `http://127.0.0.1:8002/static/${sectionId}.html#id=` + encodeURIComponent(localStorage.getItem("access_token") || "")
      window.location.href = url
    } else {
      window.location.href = 'http://localhost/datasets'
    }
  }

  // 保存原始滚动样式，以便在组件销毁时恢复
  let originalBodyOverflow: string;

  // 在组件挂载时对菜单项进行分类并禁用页面滚动
  onMount(() => {
    // 保存原始滚动样式
    originalBodyOverflow = document.body.style.overflow;

    // 只在这个组件中禁用滚动
    document.body.style.overflow = 'hidden';

    // 将菜单项分配到对应的模块
    moduleCategories = moduleCategories.map(category => {
      switch(category.id) {
        case "ai_chat":
          category.items = enrichedSections.filter(s => ["ai_chat"].includes(s.id));
          break;
        case "inference":
          category.items = enrichedSections.filter(s => ["infer_point", "create_task"].includes(s.id));
          break;
        case "model_management":
          category.items = enrichedSections.filter(s => ["model_repo", "owner_repo"].includes(s.id));
          break;
        case "experiment":
          category.items = enrichedSections.filter(s => ["ab_test_combined", "prompt_lab"].includes(s.id));
          break;
        case "evaluation":
          category.items = enrichedSections.filter(s => ["eval", "dify"].includes(s.id));
          break;
        case "development":
          category.items = enrichedSections.filter(s => ["ide", "api_key"].includes(s.id));
          break;
        case "community":
          category.items = enrichedSections.filter(s => ["index_article"].includes(s.id));
          break;
      }
      return category;
    });

    // 过滤掉没有菜单项的模块
    moduleCategories = moduleCategories.filter(category => category.items.length > 0);
  });

  // 在组件销毁时恢复页面滚动
  onDestroy(() => {
    // 恢复原始滚动样式
    document.body.style.overflow = originalBodyOverflow;
  });
</script>

  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    /* 移除全局滚动限制，改为只在组件内部控制滚动 */

    .volcano-container {
      display: flex;
      height: 100vh; /* 固定高度为视口高度 */
      position: relative; /* 为固定定位的子元素提供参考 */
      overflow: hidden; /* 禁止容器内滚动 */
      width: 100%; /* 确保容器占满整个宽度 */
    }

    .nav-sidebar {
      width: 280px;
      background: #ffffff;
      box-shadow: 2px 0 12px rgba(0, 0, 0, 0.05);
      position: fixed;
      height: 100vh;
      overflow-y: auto; /* 保持侧边栏可滚动 */
      z-index: 10; /* 确保侧边栏在最上层 */
    }

    .logo {
      height: 72px;
      display: flex;
      align-items: center;
      padding: 0 24px;
      font-size: 1.25rem;
      font-weight: 600;
      color: #2563eb;
      border-bottom: 1px solid #e2e8f0;
    }

    .nav-menu {
      padding: 10px 0;
    }

    /* 模块分类样式 */
    .module-category {
      margin-bottom: 8px;
    }

    .category-header {
      display: flex;
      align-items: center;
      padding: 10px 24px;
      font-weight: 600;
      color: #1e293b;
      font-size: 0.9rem;
      border-bottom: 1px solid #f1f5f9;
      margin-bottom: 4px;
    }

    .category-icon {
      margin-right: 10px;
      font-size: 1.2rem;
    }

    .category-description {
      font-size: 0.75rem;
      color: #64748b;
      margin-top: 2px;
      padding-left: 24px;
      padding-right: 10px;
      margin-bottom: 8px;
    }

    .menu-item {
      padding: 10px 24px 10px 36px;
      margin: 2px 8px;
      border-radius: 8px;
      color: #64748b;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 0.9rem;
    }

    .menu-item.active {
      background: #eff6ff;
      color: #2563eb;
      font-weight: 500;
    }

    .menu-item:hover:not(.active) {
      background: #f8fafc;
    }

    .item-icon {
      font-size: 1.1rem;
      width: 24px;
      text-align: center;
    }

    .content-main {
      flex: 1;
      margin-left: 280px; /* 与侧边栏宽度相同 */
      height: 100vh; /* 固定高度为视口高度 */
      position: relative; /* 确保内容在背景图片上方 */
      z-index: 1;
      overflow: hidden; /* 禁止滚动 */
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* 欢迎内容样式 */
    .welcome-content {
      max-width: 800px;
      padding: 40px;
      text-align: center;
    }

    .welcome-content h1 {
      font-size: 2.5rem;
      color: #1a365d;
      margin-bottom: 16px;
      font-weight: 700;
    }

    .welcome-content p {
      font-size: 1.1rem;
      color: #4a5568;
      margin-bottom: 40px;
    }

    /* 功能卡片样式 */
    .feature-cards {
      display: flex;
      gap: 24px;
      justify-content: center;
      margin-bottom: 40px;
    }

    .feature-card {
      background: white;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
      width: 220px;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .feature-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
    }

    .card-icon {
      font-size: 2.5rem;
      margin-bottom: 16px;
    }

    .feature-card h3 {
      font-size: 1.2rem;
      color: #2d3748;
      margin-bottom: 12px;
      font-weight: 600;
    }

    .feature-card p {
      font-size: 0.9rem;
      color: #718096;
      margin-bottom: 0;
    }

    .welcome-footer {
      margin-top: 40px;
    }

    .welcome-footer p {
      font-size: 1rem;
      color: #4a5568;
      font-style: italic;
    }

    /* 按钮样式 */
    .btn-jump {
      padding: 12px 24px;
      background-color: #2563eb;
      color: white;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      font-size: 1rem;
      transition: background-color 0.3s ease;
      display: inline-block;
      margin-top: 20px;
      margin-left: 24px;
      margin-bottom: 20px;
    }

    .btn-jump:hover {
      background-color: #1d4ed8;
    }

    .btn-jump:focus {
      outline: none;
    }

    .banner-right {
      /* 使用更柔和的渐变背景 */
      background: linear-gradient(135deg, #f8fafc 0%, #e6f0fd 100%);
      height: 100vh;
      position: fixed;
      right: 0;
      top: 0;
      width: calc(100% - 280px); /* 减去侧边栏宽度 */
      z-index: -1; /* 确保背景在内容后面 */
      overflow: hidden; /* 确保装饰元素不会溢出 */
    }

    /* 添加装饰元素 - 顶部波浪 */
    .banner-right::before {
      content: '';
      position: absolute;
      width: 100%;
      height: 300px;
      background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%23e6f0fd" fill-opacity="0.4" d="M0,192L48,176C96,160,192,128,288,122.7C384,117,480,139,576,165.3C672,192,768,224,864,213.3C960,203,1056,149,1152,138.7C1248,128,1344,160,1392,176L1440,192L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z"></path></svg>');
      background-size: cover;
      background-repeat: no-repeat;
      top: 0;
      left: 0;
      opacity: 0.8;
    }

    /* 添加装饰元素 - 底部波浪 */
    .banner-right::after {
      content: '';
      position: absolute;
      width: 100%;
      height: 300px;
      background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%234a90e2" fill-opacity="0.1" d="M0,64L48,80C96,96,192,128,288,128C384,128,480,96,576,90.7C672,85,768,107,864,144C960,181,1056,235,1152,234.7C1248,235,1344,181,1392,154.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
      background-size: cover;
      background-repeat: no-repeat;
      bottom: 0;
      left: 0;
      opacity: 0.8;
    }

    /* 添加浮动圆点装饰 */
    .banner-right .dots {
      position: absolute;
      width: 100%;
      height: 100%;
      overflow: hidden;
      z-index: -1;
    }

    .dot {
      position: absolute;
      border-radius: 50%;
      background-color: rgba(74, 144, 226, 0.1);
    }

    .dot:nth-child(1) {
      width: 100px;
      height: 100px;
      top: 10%;
      right: 10%;
    }

    .dot:nth-child(2) {
      width: 150px;
      height: 150px;
      bottom: 30%;
      right: 20%;
      background-color: rgba(74, 144, 226, 0.05);
    }

    .dot:nth-child(3) {
      width: 80px;
      height: 80px;
      top: 40%;
      right: 30%;
      background-color: rgba(74, 144, 226, 0.08);
    }

    /* 工具提示样式 */
    .tooltip {
      position: relative;
    }

    .tooltip:hover .tooltip-text {
      visibility: visible;
      opacity: 1;
    }

    .tooltip-text {
      visibility: hidden;
      width: 200px;
      background-color: #333;
      color: #fff;
      text-align: center;
      border-radius: 6px;
      padding: 8px;
      position: absolute;
      z-index: 1;
      left: 110%;
      top: 0;
      opacity: 0;
      transition: opacity 0.3s;
      font-size: 0.8rem;
      pointer-events: none;
    }

    .tooltip-text::after {
      content: "";
      position: absolute;
      top: 50%;
      right: 100%;
      margin-top: -5px;
      border-width: 5px;
      border-style: solid;
      border-color: transparent #333 transparent transparent;
    }
  </style>
  <div class="volcano-container">
    {#if !activeSection}
      <!-- 左侧导航 -->
      <nav class="nav-sidebar">
        <div class="logo">
          <span>开发者社区</span>
        </div>

        <div class="nav-menu">
          {#each moduleCategories as category}
            <div class="module-category">
              <div class="category-header">
                <span class="category-icon">{category.icon}</span>
                <span>{category.name}</span>
              </div>
              <div class="category-description">
                {category.description}
              </div>

              {#each category.items as item}
                <button
                  class="menu-item {activeSection === item.id ? 'active' : ''}"
                  on:click={() => handleClick(item)}
                  aria-label={item.name}
                >
                  <span class="item-icon">{getItemIcon(item.id)}</span>
                  <span>{item.name}</span>
                  <div class="tooltip">
                    <div class="tooltip-text">
                      {item.description || '点击进入' + item.name}
                    </div>
                  </div>
                </button>
              {/each}
            </div>
          {/each}
        </div>

        <button class="btn-jump" on:click={() => {
          // 在导航前恢复滚动功能
          document.body.style.overflow = originalBodyOverflow;
          goto("/eval");
        }}>
          返回大模型平台
        </button>
      </nav>

      <!-- 右侧图片背景 -->
      <div class="banner-right">
        <div class="dots">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </div>

      <!-- 右侧内容区域 -->
      <main class="content-main">
        <div class="welcome-content">
          <h1>欢迎来到开发者社区</h1>
          <p>这里是大模型开发者的交流平台，探索AI的无限可能</p>

          <div class="feature-cards">
            <div class="feature-card">
              <div class="card-icon">🤖</div>
              <h3>AI对话模块</h3>
              <p>支持多模态交互与高并发流式响应</p>
            </div>

            <div class="feature-card">
              <div class="card-icon">🧠</div>
              <h3>推理模块</h3>
              <p>提供统一的模型推理接入点</p>
            </div>

            <div class="feature-card">
              <div class="card-icon">📦</div>
              <h3>模型管理模块</h3>
              <p>构建完整模型生命周期管理系统</p>
            </div>
          </div>

          <div class="welcome-footer">
            <p>从左侧菜单选择功能开始探索</p>
          </div>
        </div>
      </main>
    {/if}
  </div>