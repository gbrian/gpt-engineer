import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'

import vuePugPlugin from 'vue-pug-plugin'

const API_URL = process.env.API_URL
console.log("API_URL", API_URL)
// https://vitejs.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: API_URL,
        changeOrigin: true,
      },
    }
  },
  plugins: [
    vue(),
    vueJsx(),
    vuePugPlugin
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
