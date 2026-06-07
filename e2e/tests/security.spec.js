const { test, expect } = require('@playwright/test');

// ── Security Edge Cases ──

test('SQL injection attempt returns error not 200', async ({ request }) => {
  const response = await request.post('http://164.92.172.10:5000/api/user/login', {
    data: { email: "' OR 1=1 --", password: "' OR 1=1 --" }
  });
  expect(response.status()).not.toBe(200);
});

test('XSS attempt in login returns error', async ({ request }) => {
  const response = await request.post('http://164.92.172.10:5000/api/user/login', {
    data: { email: "<script>alert('xss')</script>", password: "test" }
  });
  expect(response.status()).not.toBe(200);
});

test('empty body request returns error', async ({ request }) => {
  const response = await request.post('http://164.92.172.10:5000/api/user/login', {
    data: {}
  });
  expect([400, 401, 404, 500]).toContain(response.status());
});

test('server does not expose stack trace on error', async ({ request }) => {
  const response = await request.get('http://164.92.172.10:5000/nonexistent');
  const text = await response.text();
  expect(text).not.toContain('at Object.');
  expect(text).not.toContain('node_modules');
});

test('server response time is acceptable', async ({ request }) => {
  const start = Date.now();
  await request.get('http://164.92.172.10:5000/');
  const duration = Date.now() - start;
  expect(duration).toBeLessThan(3000);
});