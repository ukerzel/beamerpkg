import { defineConfig } from 'vite';

export default defineConfig({
    base: './',
    build: {
        outDir: '../../src/beamerpkg/static/spatial',
        emptyOutDir: true,
        copyPublicDir: false,
        // The main chunk (~775 kB, mostly PDF.js plus React and zod) exceeds
        // Vite's default 500 kB warning, a heuristic for sites downloaded over a
        // network. `beamerpkg spatial` serves these files from the installed
        // package on 127.0.0.1, and the viewer needs PDF.js at once, so code
        // splitting would gain nothing. The raised limit only silences that
        // warning; the output is unchanged.
        chunkSizeWarningLimit: 1500,
    },
});
