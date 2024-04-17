import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import compression from 'vite-plugin-compression'

export default defineConfig({
    plugins: [
      sveltekit(), compression({
        algorithm: 'gzip',
        threshold: 10240,
    })
    ],
    build: {
        minify: 'terser', // enable minification
        chunkSizeWarningLimit: 512, // set warning limit to 512kb
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://backend:8000/',
                changeOrigin: true,
                rewrite: path => path.replace(/^\/api/, '')
            },
            '/net': {
                target: 'http://proxy:80/',
                changeOrigin: true,
                rewrite: path => path.replace(/^\/net/, '/net')
            }
        }
    }
});