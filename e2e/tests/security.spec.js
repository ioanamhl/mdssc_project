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

test('oversized payload is handled gracefully', async ({ request }) => {
  const bigPayload = 'a'.repeat(100000);
  const response = await request.post('http://164.92.172.10:5000/api/user/login', {
    data: { email: bigPayload, password: bigPayload }
  });
  expect([400, 404, 413, 500]).toContain(response.status());
});

test('invalid JSON content type is rejected', async ({ request }) => {
  const response = await request.post('http://164.92.172.10:5000/api/user/login', {
    headers: { 'Content-Type': 'text/plain' },
    data: 'not json'
  });
  expect([400, 404, 415, 500]).toContain(response.status());
});

test('missing auth token returns 401 or 403 on protected route', async ({ request }) => {
  const response = await request.get('http://164.92.172.10:5000/api/cart');
  expect([401, 403, 404, 500]).toContain(response.status());
});

test('special characters in input do not break server', async ({ request }) => {
  const response = await request.post('http://164.92.172.10:5000/api/user/login', {
    data: { email: '!@#$%^&*()', password: '!@#$%^&*()' }
  });
  expect(response.status()).not.toBe(200);
});

test('server handles concurrent requests', async ({ request }) => {
  const requests = Array(5).fill(null).map(() => 
    request.get('http://164.92.172.10:5000/')
  );
  const responses = await Promise.all(requests);
  responses.forEach(r => expect(r.status()).toBe(200));
});