<script lang="ts">
    import { getHtmlContent } from '$lib/htmlContents'; // 引入获取 HTML 内容的函数
  
    let selectedFeature = '';   // 当前选中的功能
    let htmlContent = '';       // 用于存储获取到的 HTML 内容
    let loading = false;        // 控制加载状态
  
    // 根据选中的功能，获取对应的 HTML 内容
    const loadContent = async (feature: string) => {
      loading = true;
      selectedFeature = feature;
      htmlContent = await getHtmlContent(feature); // 调用模拟的 API 获取 HTML 内容
      loading = false;
    };
  </script>
  
  <style>
    .menu {
      width: 200px;
      background-color: #f1f1f1;
      padding: 20px;
    }
  
    .content {
      padding: 20px;
      border-left: 2px solid #ddd;
      flex-grow: 1;
    }
  
    .container {
      display: flex;
      height: 100vh;
    }
  
    .menu button {
      width: 100%;
      padding: 10px;
      margin-bottom: 10px;
      background-color: #3498db;
      color: white;
      border: none;
      cursor: pointer;
      text-align: left;
    }
  
    .menu button:hover {
      background-color: #2980b9;
    }
  
    .loading {
      text-align: center;
      margin-top: 20px;
    }
  </style>
  
  <div class="container">
    <!-- 左侧菜单栏 -->
    <div class="menu">
      <button on:click={() => loadContent('featureA')}>Feature A</button>
      <button on:click={() => loadContent('featureB')}>Feature B</button>
      <button on:click={() => loadContent('featureC')}>Feature C</button>
    </div>
  
    <!-- 右侧显示区域 -->
    <div class="content">
      {#if loading}
        <div class="loading">
          <p>Loading...</p>
        </div>
      {:else}
        <div class="html-content">
          {@html htmlContent}
        </div>
      {/if}
    </div>
  </div>
  