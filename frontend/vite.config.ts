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
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    // Generate source maps for production debugging
    sourcemap: true,
    // Optimize chunks
    rollupOptions: {
      output: {
        // Manual chunks for better caching
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
        },
      },
    },
  },
  // Environment variables configuration
  define: {
    // Make build-time variables available
    __VITE_API_BASE_URL__: JSON.stringify(process.env.VITE_API_BASE_URL || 'http://localhost:8000'),
  },
});
