import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Optional: set API_PROXY (e.g. https://cinema.damian-kowalczyk.dev) together with VITE_GATEWAY_URL=/api
// to run the local dev server against the production API — handy for checking the layout on a phone
// in the same Wi-Fi (`npm run dev -- --host`). Login won't work this way (Auth0 calls back to production).
const apiProxy = process.env.API_PROXY

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    strictPort: true,
    proxy: apiProxy ? { '/api': { target: apiProxy, changeOrigin: true } } : undefined,
  },
})
