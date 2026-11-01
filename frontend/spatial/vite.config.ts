import { defineConfig } from 'vite';

export default defineConfig({
    base: './',
    build: {
        outDir: '../../src/beamerpkg/static/spatial',
        emptyOutDir: true,
        copyPublicDir: false,
    },
});
