const { test, expect } = require('@playwright/test');

test('backend health check', async ({ request }) => {
  const response = await request.get('http://164.92.172.10:5000/');
  expect(response.status()).toBe(200);
  const text = await response.text();
  expect(text).toContain('running');
});

test('GET /api/product returneaza produse', async ({ request }) => {
  const response = await request.get('http://164.92.172.10:5000/api/product');
  expect(response.status()).toBe(200);
});

test('POST /api/user/login fara credentiale returneaza eroare', async ({ request }) => {
  const response = await request.post('http://164.92.172.10:5000/api/user/login', {
    data: {}
  });
  expect(response.status()).toBe(400);
});