import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { createHtmlPlugin } from 'vite-plugin-html'

export default defineConfig({
  plugins: [
    vue(),
    createHtmlPlugin({
      inject: {
        data: {
          VITE_SITE_NAME: process.env.VITE_SITE_NAME,
          VITE_SITE_DESCRIPTION: process.env.VITE_SITE_DESCRIPTION,
          VITE_SITE_URL: process.env.VITE_SITE_URL,
          VITE_CONTACT_EMAIL: process.env.VITE_CONTACT_EMAIL,
          VITE_CONTACT_PHONE: process.env.VITE_CONTACT_PHONE
        }
      }
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
