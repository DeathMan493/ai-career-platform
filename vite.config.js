import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => ({
    plugins: [react()],
    build: {
        sourcemap: false
    },
    esbuild: {
        drop: mode === "production" ? ["console", "debugger"] : []
    }
}));
