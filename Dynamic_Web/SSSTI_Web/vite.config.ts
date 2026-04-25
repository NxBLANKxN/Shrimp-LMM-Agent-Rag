import { defineConfig } from 'vite'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import tailwindcss from "@tailwindcss/vite"
import babel from '@rolldown/plugin-babel'
import path from "path"

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    babel({ presets: [reactCompilerPreset()] })
  ],
  resolve: {
    alias: {
      // 關鍵設定：告訴 Vite @ 代表 src 資料夾
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
