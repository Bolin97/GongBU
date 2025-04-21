// src/lib/htmlContents.js

export const getHtmlContent = async (feature) => {
    // 模拟根据不同的功能名称返回不同的 HTML 内容
    const contentMap = {
      featureA: "<h2>Feature A</h2><p>This is the content for Feature A.</p>",
      featureB: "<h2>Feature B</h2><p>This is the content for Feature B.</p>",
      featureC: "<h2>Feature C</h2><p>This is the content for Feature C.</p>"
    };
  
    // 返回模拟的数据
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(contentMap[feature] || "<p>No content available.</p>");
      }, 500);
    });
  };
  