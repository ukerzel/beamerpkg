import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests', workers: 1, timeout: 60_000,
  use: { headless: true, viewport: { width: 1280, height: 800 }, trace: 'retain-on-failure' },
  webServer: { command: 'npm run dev -- --port 5173 --strictPort', url: 'http://127.0.0.1:5173/probe.html', reuseExistingServer: false },
});
