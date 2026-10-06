import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/auth': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
       '/predict': {
         target: 'http://backend:8000',
         changeOrigin: true,
      },
      '/monitoring': {
        target: 'http://backend:8000',
        changeOrigin: true,
}
    }
  }
})