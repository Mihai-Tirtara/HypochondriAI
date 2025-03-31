import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite'


export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      // Example alias setup
    },
  },
  server: {
    port: 3000, // Optional: Match CRA's default port
  },
});
