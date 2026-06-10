const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  use: {
    baseURL: process.env.BASE_URL || process.env.E2E_BASE_URL_FALLBACK || 'http://localhost:3000',
    headless: true,
  },
  reporter: [['html', { outputFolder: 'playwright-report' }]],
});