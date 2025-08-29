import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    allowedHosts: ["2b2fdd42-277d-49b2-b701-ea4fa70e62be-00-1lox23r3b1qyl.kirk.replit.dev"],
    host: "0.0.0.0",
    port: 5000,
    hmr: {
      port: 5000,
    },
  },
  plugins: [
    react(),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
