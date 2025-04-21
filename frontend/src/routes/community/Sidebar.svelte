<script>
  import { goto } from '$app/navigation';

    export let sections = [];
    export let activeSection = "";
    
    const handleClick = (section) => {
      activeSection = section.id;
      fetchContent(section.id);
    };
  
    import axios from 'axios';

    // async function fetchContent(sectionId) {
    //   // try {
    //   //   // 使用 axios 发起 GET 请求
    //   //   const response = await axios.get(`/api/static/${sectionId}`);
    //   //   const html = response.data;  // 从响应数据中获取 html 字段
    //   //   contentHtml = html;  // 更新 contentHtml
    //   // } catch (error) {
    //   //   console.error('Failed to load content:', error);  // 错误处理
    //   // }
    //   goto(`/api/static/${sectionId}`)
    // }


    // 修改后的 fetchContent 函数
    async function fetchContent(sectionId) {
      // 使用前端路由跳转而非直接调用 API
      goto(`/community/${sectionId}`);
    }

    
    // let contentHtml = "";
  </script>
  
  <style>
    /* 保持原有CSS不变 */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
  
    .volcano-container {
      display: flex;
      min-height: 100vh;
    }
  
    .nav-sidebar {
      width: 240px;
      background: #ffffff;
      box-shadow: 2px 0 12px rgba(0, 0, 0, 0.05);
      position: fixed;
      height: 100vh;
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
      padding: 20px 0;
    }
  
    .menu-item {
      padding: 12px 24px;
      margin: 4px 12px;
      border-radius: 8px;
      color: #64748b;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 12px;
    }
  
    .menu-item.active {
      background: #eff6ff;
      color: #2563eb;
      font-weight: 500;
    }
  
    .menu-item:hover:not(.active) {
      background: #f8fafc;
    }
  
    .content-main {
      flex: 1;
      background: #f8fafc;
    }

    /* 新增按钮样式 */
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
    }

    .btn-jump:hover {
      background-color: #1d4ed8;
    }

    .btn-jump:focus {
      outline: none;
    }

    .banner-right {
      background-image: url('/community3.png');
      background-repeat: no-repeat;
      background-position: right center;
      background-size: cover;
      height: 100vh;
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
          {#each sections as section}
            <div 
              class="menu-item {activeSection === section.id ? 'active' : ''}"
              on:click={() => handleClick(section)}
            >
              <span>{section.name}</span>
            </div>
          {/each}
        </div>

        <button class="btn-jump" on:click={() => goto("/model")}>
          返回大模型平台
        </button>
      </nav>

        <!-- 右侧图片 -->
      <main class="content-main banner-right">
      </main>
    {/if}
    
  
    <!-- 动态内容区域
    <main class="content-main">
      {@html contentHtml}
    </main> -->
  </div>