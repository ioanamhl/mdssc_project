const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  use: {
    baseURL: process.env.BASE_URL || 'http://164.92.172.10:3001',
    headless: true,
  },
  reporter: [['html', { outputFolder: 'playwright-report' }]],
});