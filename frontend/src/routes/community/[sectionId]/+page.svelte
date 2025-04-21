<script lang="ts">
    import { onMount } from "svelte";
    import axios from "axios";
    import { page } from '$app/stores';
    
    export let sectionId;
    let contentHtml = "";
    // let sectionId = $page.params.sectionId;
    console.log('路由参数 sectionId:', sectionId);
    // 动态执行脚本的函数
    const executeScripts = (html) => {
      // 提取所有 script 标签内容
      const scripts = html.match(/<script\b[^>]*>([\s\S]*?)<\/script>/gm) || [];
      
      // 执行每个脚本
      scripts.forEach(script => {
        const code = script
          .replace(/<\/?script>/g, '')
          .replace(/\/\/# sourceMappingURL=.+?$/gm, '');
        
        try {
          // 使用 eval 执行
          window.eval(code);
        } catch (err) {
          console.error('脚本执行错误:', err);
        }
      });
  
      // 返回清理后的 HTML（移除 script 标签）
      return html.replace(/<script\b[^>]*>([\s\S]*?)<\/script>/gm, '');
    };
  
    onMount(async () => {
      try {
        const response = await axios.get(`/api/static/${sectionId}`);
        // 处理内容并执行脚本
        const processedHtml = executeScripts(response.data.html); 
        contentHtml = processedHtml;
        
        // 动态加载外部脚本
        const externalScripts = response.data.html.match(/<script src="(.*?)"><\/script>/g) || [];
        externalScripts.forEach(script => {
          const src = script.match(/src="(.*?)"/)[1];
          const scriptEl = document.createElement('script');
          scriptEl.src = src;
          document.head.appendChild(scriptEl);
        });
      } catch (error) {
        console.error("加载失败:", error);
      }
    });
  </script>
  
  {#if !sectionId}
    <div>错误：未获取到 sectionId 参数</div>
  {/if}
  {#if !contentHtml}
    <div class="loading-spinner">加载中...</div>
  {/if}
  <div class="content-container">
    {@html contentHtml}
  </div>