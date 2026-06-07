const { test, expect } = require('@playwright/test');

test('backend is accessible', async ({ request }) => {
  const response = await request.get('http://164.92.172.10:5000/');
  expect(response.status()).toBe(200);
});

test('backend response is not empty', async ({ request }) => {
  const response = await request.get('http://164.92.172.10:5000/');
  const text = await response.text();
  expect(text.length).toBeGreaterThan(0);
});