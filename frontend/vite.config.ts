import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import compression from 'vite-plugin-compression'

export default defineConfig({
	plugins: [sveltekit(), compression({
		algorithm: 'gzip',
		threshold: 10240,
	})],
	build: {
		minify: 'terser', // enable minification
		chunkSizeWarningLimit: 512, // set warning limit to 512kb
		rollupOptions: {
			output:{
				manualChunks(id) {
					if (id.includes('node_modules')) {
						return id.toString().split('node_modules/')[1].split('/')[0].toString();
					}
				}
			}
		}
	}
});
