const { test, expect } = require('@playwright/test');

test('BAD TEST: vulnerable dependency lodash 4.17.15 should be detected', async ({ request }) => {
  // This test documents that lodash 4.17.15 has known vulnerabilities
  // CVE-2021-23337 (Command Injection) - severity: HIGH
  // CVE-2020-28500 (ReDoS) - severity: MODERATE
  // npm audit should detect these and flag them in the pipeline
  const response = await request.get('http://164.92.172.10:5000/');
  expect(response.status()).toBe(200);
  console.log('WARNING: lodash 4.17.15 is intentionally vulnerable for demo purposes');
});

test('BAD TEST: server should still respond despite vulnerable dependencies', async ({ request }) => {
  const response = await request.get('http://164.92.172.10:5000/');
  expect(response.status()).toBe(200);
});