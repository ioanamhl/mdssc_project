const { test, expect } = require('@playwright/test');

test('homepage se incarca', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/.+/);
});

test('pagina returneaza status 200', async ({ page }) => {
  const response = await page.goto('/');
  expect(response.status()).toBe(200);
});