import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import compression from "vite-plugin-compression";

export default defineConfig({
  plugins: [
    sveltekit(),
    compression({
      algorithm: "gzip",
      threshold: 10240,
    }),
  ],
  build: {
    minify: "terser", // enable minification
    chunkSizeWarningLimit: 512, // set warning limit to 512kb
  },
  server: {
    host: '0.0.0.0',
    proxy: {
      "/api": {
        target: "http://backend:8000/",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      "/net": {
        target: "http://proxy:81/",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/net/, "/net"),
      },
      "/dify": {
        target: "http://nginx:80/",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/dify/, ""), // 去掉 /dify 前缀
      },
      "/_next": {
        target: "http://nginx:80/",
        changeOrigin: true,
      },
    },
  },
});
