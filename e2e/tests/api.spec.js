const { test, expect } = require('@playwright/test');

test('backend health check returns 200', async ({ request }) => {
  const response = await request.get('http://164.92.172.10:5000/');
  expect(response.status()).toBe(200);
});

test('backend returns non-empty response body', async ({ request }) => {
  const response = await request.get('http://164.92.172.10:5000/');
  const text = await response.text();
  expect(text.length).toBeGreaterThan(0);
});

test('unknown route returns 404', async ({ request }) => {
  const response = await request.get('http://164.92.172.10:5000/nonexistent-route');
  expect(response.status()).toBe(404);
});

test('POST /api/user/login without credentials returns error', async ({ request }) => {
  const response = await request.post('http://164.92.172.10:5000/api/user/login', {
    data: {}
  });
  expect([400, 401, 404, 500]).toContain(response.status());
});

test('POST /api/user/register without body returns error', async ({ request }) => {
  const response = await request.post('http://164.92.172.10:5000/api/user/register', {
    data: {}
  });
  expect([400, 401, 404, 500]).toContain(response.status());
});