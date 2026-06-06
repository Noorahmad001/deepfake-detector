import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  css: {
    postcss: './postcss.config.js',
  },
  server: {
    proxy: {
      '/api': {
        target: 'https://deepfake-detector-2-5zeq.onrender.com',
        changeOrigin: true,
      },
      '/health': {
        target: 'https://deepfake-detector-2-5zeq.onrender.com',
        changeOrigin: true,
      },
    },
  },
})
