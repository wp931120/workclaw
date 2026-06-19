import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3010,
    allowedHosts: ['3dd85b04495015.lhr.life', '53c261865c9ff7.lhr.life', 'workclaw-wp931120.loca.lt'],
    proxy: {
      '/api': {
        target: 'http://localhost:8010',
        changeOrigin: true,
      },
    },
  },
})