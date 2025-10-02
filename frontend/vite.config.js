import {defineConfig} from 'vite'
import react from '@vitejs/plugin-react'
import tailwind from "@tailwindcss/vite";
import path from "path"

export default defineConfig({
    plugins: [react(), tailwind()],
    resolve: {
        alias: {
            // eslint-disable-next-line no-undef
            "@": path.resolve(__dirname, "./src"),
        },
    },
})