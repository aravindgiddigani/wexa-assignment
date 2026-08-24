import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'https://wexa-assignment-1.onrender.com/api',
        changeOrigin: true,
      }
    }
  }
})
